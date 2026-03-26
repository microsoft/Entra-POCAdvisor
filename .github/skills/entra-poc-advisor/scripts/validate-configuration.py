#!/usr/bin/env python3
"""Validate tenant configuration against target state.

Takes JSON input (stdin or --input argument) with current and target
configuration for each component, compares them, and produces a Markdown
validation report with per-component status.

Status values:
  - Configured: all target properties match current state
  - Partially Configured: some target properties match, others do not
  - Missing: component has no current configuration at all
  - Misconfigured: component exists but key properties contradict the target

Exit code: 0 if all components are Configured, 1 if any gaps exist.

Input format:
{
  "scenario": "...",
  "components": [
    {
      "name": "...",
      "target": { "property": "value", ... },
      "current": { "property": "value", ... }  // or null/empty for missing
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Status constants
STATUS_CONFIGURED = "Configured"
STATUS_PARTIAL = "Partially Configured"
STATUS_MISSING = "Missing"
STATUS_MISCONFIGURED = "Misconfigured"

STATUS_ICONS = {
    STATUS_CONFIGURED: "PASS",
    STATUS_PARTIAL: "PARTIAL",
    STATUS_MISSING: "MISSING",
    STATUS_MISCONFIGURED: "MISCONFIG",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate tenant configuration against target state.",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to JSON input file. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write the Markdown report. If omitted, writes to stdout.",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Path to write structured JSON results (for piping to gap report).",
    )
    return parser.parse_args()


def load_input(input_path: str | None) -> dict[str, Any]:
    """Load and return JSON input from a file or stdin."""
    try:
        if input_path:
            path = Path(input_path)
            if not path.exists():
                print(f"Error: Input file not found: {input_path}", file=sys.stderr)
                sys.exit(2)
            raw = path.read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON input: {exc}", file=sys.stderr)
        sys.exit(2)


def validate_input(data: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Validate the input structure. Returns (scenario, components).

    Exits with code 2 on validation errors.
    """
    if "scenario" not in data:
        print('Error: Input JSON must contain a "scenario" field.', file=sys.stderr)
        sys.exit(2)

    if "components" not in data:
        print('Error: Input JSON must contain a "components" array.', file=sys.stderr)
        sys.exit(2)

    components = data["components"]
    if not isinstance(components, list) or len(components) == 0:
        print('Error: "components" must be a non-empty JSON array.', file=sys.stderr)
        sys.exit(2)

    for i, comp in enumerate(components):
        if "name" not in comp:
            print(
                f'Error: Component at index {i} is missing required field "name".',
                file=sys.stderr,
            )
            sys.exit(2)
        if "target" not in comp:
            print(
                f'Error: Component at index {i} ("{comp["name"]}") is missing "target".',
                file=sys.stderr,
            )
            sys.exit(2)
        # "current" is optional -- absence means missing configuration
        if "current" not in comp:
            comp["current"] = None

    return data["scenario"], components


def compare_values(target_val: Any, current_val: Any) -> bool:
    """Compare a target value against a current value.

    Performs case-insensitive comparison for strings, direct comparison
    for other types. For nested dicts, compares recursively.
    """
    if isinstance(target_val, str) and isinstance(current_val, str):
        return target_val.strip().lower() == current_val.strip().lower()
    if isinstance(target_val, dict) and isinstance(current_val, dict):
        return all(
            key in current_val and compare_values(val, current_val[key])
            for key, val in target_val.items()
        )
    if isinstance(target_val, list) and isinstance(current_val, list):
        # Check that all target items are present in current (order-independent)
        return all(any(compare_values(tv, cv) for cv in current_val) for tv in target_val)
    return target_val == current_val


def evaluate_component(
    component: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate a single component's current state vs target.

    Returns an enriched component dict with status, matches, and gaps.
    """
    name = component["name"]
    target = component["target"]
    current = component["current"]

    # Missing: current is None, empty dict, or empty
    if current is None or (isinstance(current, dict) and len(current) == 0):
        return {
            "name": name,
            "status": STATUS_MISSING,
            "target": target,
            "current": current if current else {},
            "matches": [],
            "gaps": list(target.keys()) if isinstance(target, dict) else ["entire component"],
            "details": [],
        }

    if not isinstance(target, dict) or not isinstance(current, dict):
        # Non-dict comparison: simple match/mismatch
        match = compare_values(target, current)
        return {
            "name": name,
            "status": STATUS_CONFIGURED if match else STATUS_MISCONFIGURED,
            "target": target,
            "current": current,
            "matches": ["value"] if match else [],
            "gaps": [] if match else ["value"],
            "details": [] if match else [
                {"property": "value", "target": target, "current": current}
            ],
        }

    # Dict-based comparison
    matches: list[str] = []
    gaps: list[str] = []
    details: list[dict[str, Any]] = []
    misconfigs: list[str] = []

    for key, target_val in target.items():
        if key not in current:
            gaps.append(key)
            details.append({
                "property": key,
                "target": target_val,
                "current": None,
                "issue": "missing",
            })
        elif compare_values(target_val, current[key]):
            matches.append(key)
        else:
            # Property exists but value differs
            misconfigs.append(key)
            details.append({
                "property": key,
                "target": target_val,
                "current": current[key],
                "issue": "mismatch",
            })

    total_props = len(target)
    matched_count = len(matches)

    if matched_count == total_props:
        status = STATUS_CONFIGURED
    elif matched_count == 0 and len(misconfigs) > 0:
        status = STATUS_MISCONFIGURED
    elif matched_count == 0:
        status = STATUS_MISSING
    else:
        # Some match, some don't: distinguish partial from misconfigured
        if len(misconfigs) > 0:
            status = STATUS_MISCONFIGURED if matched_count < len(misconfigs) else STATUS_PARTIAL
        else:
            status = STATUS_PARTIAL

    return {
        "name": name,
        "status": status,
        "target": target,
        "current": current,
        "matches": matches,
        "gaps": gaps + misconfigs,
        "details": details,
    }


def generate_report(
    scenario: str,
    results: list[dict[str, Any]],
) -> str:
    """Generate the Markdown validation report."""
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    total = len(results)
    configured = sum(1 for r in results if r["status"] == STATUS_CONFIGURED)
    partial = sum(1 for r in results if r["status"] == STATUS_PARTIAL)
    missing = sum(1 for r in results if r["status"] == STATUS_MISSING)
    misconfigured = sum(1 for r in results if r["status"] == STATUS_MISCONFIGURED)
    all_good = configured == total

    # Title
    lines.append("# Configuration Validation Report")
    lines.append("")
    lines.append(f"**Scenario:** {scenario}  ")
    lines.append(f"**Generated:** {now}  ")
    lines.append(f"**Components evaluated:** {total}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    pct = round(configured / total * 100) if total > 0 else 0
    lines.append(f"**Configuration completeness: {pct}%**")
    lines.append("")

    if all_good:
        lines.append(
            "All components are configured as expected. "
            "The tenant matches the target state for this scenario."
        )
    else:
        lines.append(
            f"{configured} of {total} components fully configured. "
            f"Gaps remain in {total - configured} component(s)."
        )
    lines.append("")

    # Summary table
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Configured | {configured} |")
    lines.append(f"| Partially Configured | {partial} |")
    lines.append(f"| Missing | {missing} |")
    lines.append(f"| Misconfigured | {misconfigured} |")
    lines.append("")

    # Component status table
    lines.append("## Component Status")
    lines.append("")
    lines.append("| Component | Status | Matched | Gaps |")
    lines.append("|-----------|--------|---------|------|")

    for r in results:
        icon = STATUS_ICONS[r["status"]]
        name = r["name"]
        matched = len(r["matches"])
        gap_count = len(r["gaps"])
        target_count = (
            len(r["target"]) if isinstance(r["target"], dict) else 1
        )
        lines.append(
            f"| {name} | {icon} | {matched}/{target_count} | {gap_count} |"
        )
    lines.append("")

    # Detailed findings for non-configured components
    non_configured = [r for r in results if r["status"] != STATUS_CONFIGURED]
    if non_configured:
        lines.append("## Detailed Findings")
        lines.append("")

        for r in non_configured:
            lines.append(f"### {r['name']}")
            lines.append("")
            lines.append(f"**Status:** {r['status']}")
            lines.append("")

            if r["details"]:
                lines.append("| Property | Expected | Current | Issue |")
                lines.append("|----------|----------|---------|-------|")
                for d in r["details"]:
                    prop = d["property"]
                    expected = _format_value(d["target"])
                    current = _format_value(d["current"])
                    issue = d["issue"]
                    lines.append(f"| {prop} | {expected} | {current} | {issue} |")
                lines.append("")
            elif r["status"] == STATUS_MISSING:
                lines.append(
                    "This component has no current configuration. "
                    "All target properties need to be configured."
                )
                lines.append("")
                if isinstance(r["target"], dict):
                    lines.append("**Required configuration:**")
                    lines.append("")
                    for key, val in r["target"].items():
                        lines.append(f"- `{key}`: `{_format_value(val)}`")
                    lines.append("")

    # Next steps
    lines.append("## Next Steps")
    lines.append("")
    if all_good:
        lines.append(
            "Configuration validated. Proceed to **Phase 5: Testing**."
        )
    else:
        lines.append(
            "1. Review the detailed findings above\n"
            "2. Use `generate-gap-report.py` for a complete gap analysis with remediation steps\n"
            "3. Apply the required configuration changes\n"
            "4. Re-validate to confirm all components are correctly configured"
        )
    lines.append("")

    return "\n".join(lines)


def _format_value(val: Any) -> str:
    """Format a value for display in a Markdown table cell."""
    if val is None:
        return "*(not set)*"
    if isinstance(val, dict):
        return json.dumps(val, separators=(",", ":"))
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def generate_json_output(
    scenario: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate structured JSON output suitable for piping to gap report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "scenario": scenario,
        "timestamp": now,
        "components": [
            {
                "name": r["name"],
                "status": r["status"],
                "target": r["target"],
                "current": r["current"],
                "gaps": r["gaps"],
            }
            for r in results
        ],
    }


def main() -> None:
    """Entry point."""
    args = parse_args()

    # Load and validate
    data = load_input(args.input)
    scenario, components = validate_input(data)

    # Evaluate each component
    results = [evaluate_component(comp) for comp in components]

    # Generate Markdown report
    report = generate_report(scenario, results)

    # Output Markdown
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    # Output JSON (for piping to gap report)
    if args.json_output:
        json_data = generate_json_output(scenario, results)
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(json_data, indent=2), encoding="utf-8"
        )
        print(f"JSON output written to {args.json_output}", file=sys.stderr)

    # Exit code: 1 if any component is not fully configured
    all_configured = all(r["status"] == STATUS_CONFIGURED for r in results)
    sys.exit(0 if all_configured else 1)


if __name__ == "__main__":
    main()
