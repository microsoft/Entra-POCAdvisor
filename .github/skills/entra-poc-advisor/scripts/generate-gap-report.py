#!/usr/bin/env python3
"""Generate a gap analysis report from validation results.

Takes JSON input (from validate-configuration.py --json-output or direct
input) and produces a comprehensive Markdown gap analysis report including
an executive summary, component status table, detailed findings, prioritized
remediation steps, and a Mermaid diagram.

Input format:
{
  "scenario": "...",
  "tenant": "...",          // optional
  "timestamp": "...",       // optional, defaults to now
  "components": [
    {
      "name": "...",
      "status": "Configured|Partially Configured|Missing|Misconfigured",
      "target": { ... },
      "current": { ... },
      "gaps": ["property1", "property2", ...]
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Status constants (must match validate-configuration.py)
STATUS_CONFIGURED = "Configured"
STATUS_PARTIAL = "Partially Configured"
STATUS_MISSING = "Missing"
STATUS_MISCONFIGURED = "Misconfigured"

# Priority order for remediation: most critical first
STATUS_PRIORITY = {
    STATUS_MISSING: 1,
    STATUS_MISCONFIGURED: 2,
    STATUS_PARTIAL: 3,
    STATUS_CONFIGURED: 4,
}

# Mermaid node styles by status
MERMAID_STYLES = {
    STATUS_CONFIGURED: "fill:#0d6efd,color:#fff,stroke:#0a58ca",
    STATUS_PARTIAL: "fill:#ffc107,color:#000,stroke:#cc9a06",
    STATUS_MISSING: "fill:#dc3545,color:#fff,stroke:#b02a37",
    STATUS_MISCONFIGURED: "fill:#fd7e14,color:#fff,stroke:#ca6510",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a gap analysis report from validation results.",
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


def validate_input(data: dict[str, Any]) -> tuple[str, str, str, list[dict[str, Any]]]:
    """Validate input structure. Returns (scenario, tenant, timestamp, components).

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

    valid_statuses = {STATUS_CONFIGURED, STATUS_PARTIAL, STATUS_MISSING, STATUS_MISCONFIGURED}

    for i, comp in enumerate(components):
        for field in ("name", "status"):
            if field not in comp:
                print(
                    f'Error: Component at index {i} is missing required field "{field}".',
                    file=sys.stderr,
                )
                sys.exit(2)
        if comp["status"] not in valid_statuses:
            print(
                f'Error: Component at index {i} has invalid status "{comp["status"]}". '
                f"Valid: {', '.join(sorted(valid_statuses))}",
                file=sys.stderr,
            )
            sys.exit(2)
        # Ensure optional fields have defaults
        comp.setdefault("target", {})
        comp.setdefault("current", {})
        comp.setdefault("gaps", [])

    scenario = data["scenario"]
    tenant = data.get("tenant", "*(not specified)*")
    timestamp = data.get(
        "timestamp",
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    return scenario, tenant, timestamp, components


def _sanitize_mermaid_id(name: str) -> str:
    """Convert a component name to a valid Mermaid node ID."""
    # Replace non-alphanumeric chars with underscores
    clean = re.sub(r"[^a-zA-Z0-9]", "_", name)
    # Collapse multiple underscores, strip leading/trailing
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean.lower()


def _format_value(val: Any) -> str:
    """Format a value for display in a Markdown table cell."""
    if val is None:
        return "*(not set)*"
    if isinstance(val, dict):
        return json.dumps(val, separators=(",", ":"))
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def _get_gap_detail(
    component: dict[str, Any], gap_name: str
) -> tuple[str, str]:
    """Get the target and current values for a specific gap property."""
    target = component.get("target", {})
    current = component.get("current", {})

    target_val = target.get(gap_name) if isinstance(target, dict) else None
    current_val = current.get(gap_name) if isinstance(current, dict) else None

    return _format_value(target_val), _format_value(current_val)


def compute_stats(components: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary statistics."""
    total = len(components)
    by_status: dict[str, int] = {}
    for status in [STATUS_CONFIGURED, STATUS_PARTIAL, STATUS_MISSING, STATUS_MISCONFIGURED]:
        by_status[status] = sum(1 for c in components if c["status"] == status)

    configured = by_status[STATUS_CONFIGURED]
    pct = round(configured / total * 100) if total > 0 else 0

    total_gaps = sum(len(c["gaps"]) for c in components)

    return {
        "total": total,
        "by_status": by_status,
        "configured": configured,
        "percentage": pct,
        "total_gaps": total_gaps,
    }


def generate_mermaid(components: list[dict[str, Any]]) -> str:
    """Generate a Mermaid flowchart showing component status."""
    lines: list[str] = []
    lines.append("```mermaid")
    lines.append("flowchart TB")
    lines.append("    subgraph POC[\"POC Component Status\"]")
    lines.append("        direction TB")

    # Create nodes
    for comp in components:
        node_id = _sanitize_mermaid_id(comp["name"])
        name = comp["name"]
        status = comp["status"]
        gap_count = len(comp["gaps"])

        if status == STATUS_CONFIGURED:
            label = f"{name}\\n[PASS] Configured"
        elif status == STATUS_PARTIAL:
            label = f"{name}\\n[PARTIAL] {gap_count} gaps"
        elif status == STATUS_MISSING:
            label = f"{name}\\n[MISSING] Not configured"
        else:
            label = f"{name}\\n[MISCONFIG] {gap_count} issues"

        lines.append(f'        {node_id}["{label}"]')

    lines.append("    end")
    lines.append("")

    # Apply styles
    style_groups: dict[str, list[str]] = {}
    for comp in components:
        node_id = _sanitize_mermaid_id(comp["name"])
        status = comp["status"]
        style_groups.setdefault(status, []).append(node_id)

    for status, node_ids in style_groups.items():
        style = MERMAID_STYLES[status]
        for node_id in node_ids:
            lines.append(f"    style {node_id} {style}")

    lines.append("```")
    return "\n".join(lines)


def generate_report(
    scenario: str,
    tenant: str,
    timestamp: str,
    components: list[dict[str, Any]],
) -> str:
    """Generate the complete gap analysis Markdown report."""
    lines: list[str] = []
    stats = compute_stats(components)

    # Title and metadata
    lines.append("# Gap Analysis Report")
    lines.append("")
    lines.append(f"**Scenario:** {scenario}  ")
    lines.append(f"**Tenant:** {tenant}  ")
    lines.append(f"**Generated:** {timestamp}  ")
    lines.append(f"**Components:** {stats['total']}")
    lines.append("")

    # Executive summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        f"**Overall configuration completeness: {stats['percentage']}%** "
        f"({stats['configured']} of {stats['total']} components fully configured)"
    )
    lines.append("")

    if stats["percentage"] == 100:
        lines.append(
            "All components are fully configured. The tenant matches the "
            "target state for this POC scenario. No remediation is required."
        )
    elif stats["percentage"] >= 75:
        lines.append(
            "The tenant is largely configured for this scenario. "
            f"{stats['total_gaps']} configuration gap(s) remain across "
            f"{stats['total'] - stats['configured']} component(s). "
            "Minor remediation is needed before testing."
        )
    elif stats["percentage"] >= 25:
        lines.append(
            "Significant configuration gaps exist. "
            f"{stats['total_gaps']} gap(s) across "
            f"{stats['total'] - stats['configured']} component(s) require attention. "
            "Complete the remediation steps below before proceeding to testing."
        )
    else:
        lines.append(
            "The tenant is minimally configured for this scenario. "
            f"{stats['total_gaps']} gap(s) across "
            f"{stats['total'] - stats['configured']} component(s) must be addressed. "
            "A full configuration pass is recommended."
        )
    lines.append("")

    # Status breakdown table
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    for status in [STATUS_CONFIGURED, STATUS_PARTIAL, STATUS_MISSING, STATUS_MISCONFIGURED]:
        count = stats["by_status"][status]
        if count > 0:
            lines.append(f"| {status} | {count} |")
    lines.append("")

    # Component status overview
    lines.append("## Component Status Overview")
    lines.append("")
    lines.append(generate_mermaid(components))
    lines.append("")

    # Component status table
    lines.append("## Component Status Table")
    lines.append("")
    lines.append("| # | Component | Status | Gaps |")
    lines.append("|---|-----------|--------|------|")
    for i, comp in enumerate(components, 1):
        lines.append(
            f"| {i} | {comp['name']} | {comp['status']} | {len(comp['gaps'])} |"
        )
    lines.append("")

    # Detailed findings (only for non-configured components)
    non_configured = [c for c in components if c["status"] != STATUS_CONFIGURED]
    if non_configured:
        lines.append("## Detailed Findings")
        lines.append("")

        for comp in non_configured:
            lines.append(f"### {comp['name']}")
            lines.append("")
            lines.append(f"**Status:** {comp['status']}")
            lines.append("")

            if comp["status"] == STATUS_MISSING:
                lines.append(
                    "This component has not been configured. "
                    "The entire component configuration is needed."
                )
                lines.append("")
                if isinstance(comp["target"], dict) and comp["target"]:
                    lines.append("**Target configuration:**")
                    lines.append("")
                    lines.append("| Property | Required Value |")
                    lines.append("|----------|---------------|")
                    for key, val in comp["target"].items():
                        lines.append(f"| `{key}` | `{_format_value(val)}` |")
                    lines.append("")
            else:
                # Partial or Misconfigured: show per-property gaps
                if comp["gaps"]:
                    lines.append("| Property | Expected | Current | Issue |")
                    lines.append("|----------|----------|---------|-------|")
                    for gap_name in comp["gaps"]:
                        target_str, current_str = _get_gap_detail(comp, gap_name)
                        if current_str == "*(not set)*":
                            issue = "Missing"
                        else:
                            issue = "Mismatch"
                        lines.append(
                            f"| `{gap_name}` | {target_str} | {current_str} | {issue} |"
                        )
                    lines.append("")

    # Prioritized remediation steps
    lines.append("## Remediation Steps")
    lines.append("")

    if stats["percentage"] == 100:
        lines.append("No remediation required. All components are configured.")
        lines.append("")
    else:
        lines.append(
            "Complete the following steps in priority order. "
            "Missing components should be addressed first, followed by "
            "misconfigured components, then partially configured ones."
        )
        lines.append("")

        # Sort by priority (Missing > Misconfigured > Partial)
        remediation_items = sorted(
            [c for c in components if c["status"] != STATUS_CONFIGURED],
            key=lambda c: STATUS_PRIORITY.get(c["status"], 99),
        )

        step = 1
        for comp in remediation_items:
            priority_label = _priority_label(comp["status"])
            lines.append(f"### Step {step}: {comp['name']} ({priority_label})")
            lines.append("")

            if comp["status"] == STATUS_MISSING:
                lines.append(
                    f"Configure **{comp['name']}** from scratch with the following settings:"
                )
                lines.append("")
                if isinstance(comp["target"], dict):
                    for key, val in comp["target"].items():
                        lines.append(f"- Set `{key}` to `{_format_value(val)}`")
                lines.append("")
            else:
                lines.append(
                    f"Update **{comp['name']}** to resolve {len(comp['gaps'])} gap(s):"
                )
                lines.append("")
                for gap_name in comp["gaps"]:
                    target_str, current_str = _get_gap_detail(comp, gap_name)
                    if current_str == "*(not set)*":
                        lines.append(f"- Configure `{gap_name}` to `{target_str}`")
                    else:
                        lines.append(
                            f"- Change `{gap_name}` from `{current_str}` to `{target_str}`"
                        )
                lines.append("")

            step += 1

    # Configured components (brief acknowledgment)
    configured_comps = [c for c in components if c["status"] == STATUS_CONFIGURED]
    if configured_comps:
        lines.append("## Configured Components (No Action Required)")
        lines.append("")
        for comp in configured_comps:
            lines.append(f"- **{comp['name']}** — fully configured")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "*Report generated by `generate-gap-report.py`. "
        "Re-run validation after remediation to confirm all gaps are resolved.*"
    )
    lines.append("")

    return "\n".join(lines)


def _priority_label(status: str) -> str:
    """Return a human-readable priority label for a status."""
    if status == STATUS_MISSING:
        return "Priority: High"
    if status == STATUS_MISCONFIGURED:
        return "Priority: High"
    if status == STATUS_PARTIAL:
        return "Priority: Medium"
    return "Priority: Low"


def main() -> None:
    """Entry point."""
    args = parse_args()

    # Load and validate input
    data = load_input(args.input)
    scenario, tenant, timestamp, components = validate_input(data)

    # Generate report
    report = generate_report(scenario, tenant, timestamp, components)

    # Output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
