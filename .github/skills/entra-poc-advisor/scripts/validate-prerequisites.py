#!/usr/bin/env python3
"""Validate POC prerequisites given structured input.

Takes JSON input (stdin or --input argument) with prerequisite check results
and produces a formatted Markdown prerequisite report with pass/fail summary,
detailed results, and remediation guidance.

Exit code: 0 if all checks pass, 1 if any check fails.

Input format:
{
  "checks": [
    {
      "category": "licenses|roles|infrastructure|features",
      "name": "...",
      "required": "...",
      "current": "...",
      "status": "pass|fail|warning"
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

# Valid values for structured validation
VALID_CATEGORIES = {"licenses", "roles", "infrastructure", "features"}
VALID_STATUSES = {"pass", "fail", "warning"}

# Category display order and icons
CATEGORY_ORDER = ["licenses", "roles", "infrastructure", "features"]
CATEGORY_LABELS = {
    "licenses": "Licenses",
    "roles": "Admin Roles & Permissions",
    "infrastructure": "Infrastructure",
    "features": "Feature Activation",
}
STATUS_ICONS = {
    "pass": "PASS",
    "fail": "FAIL",
    "warning": "WARN",
}

# Remediation hints keyed by category
REMEDIATION_HINTS: dict[str, str] = {
    "licenses": (
        "Navigate to **Microsoft Entra admin center > Billing > Licenses** "
        "to verify license assignments. For POC purposes, consider activating "
        "trial licenses via the Microsoft 365 admin center."
    ),
    "roles": (
        "Navigate to **Microsoft Entra admin center > Roles & admins** to "
        "assign the required roles. Use PIM (Privileged Identity Management) "
        "for time-limited role activation where available."
    ),
    "infrastructure": (
        "Review the infrastructure requirements in the scenario documentation. "
        "For Global Secure Access, ensure the connector VM meets minimum specs "
        "(Windows Server 2019+, 8 GB RAM, outbound HTTPS)."
    ),
    "features": (
        "Navigate to **Microsoft Entra admin center > Global Secure Access > "
        "Get started** to activate required features. Some features require "
        "license assignment before activation is available."
    ),
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate POC prerequisites and produce a Markdown report.",
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


def validate_input(data: dict[str, Any]) -> list[dict[str, str]]:
    """Validate the input structure and return the list of checks.

    Exits with code 2 on validation errors.
    """
    if "checks" not in data:
        print('Error: Input JSON must contain a "checks" array.', file=sys.stderr)
        sys.exit(2)

    checks = data["checks"]
    if not isinstance(checks, list):
        print('Error: "checks" must be a JSON array.', file=sys.stderr)
        sys.exit(2)

    if len(checks) == 0:
        print('Error: "checks" array is empty.', file=sys.stderr)
        sys.exit(2)

    for i, check in enumerate(checks):
        for field in ("category", "name", "required", "current", "status"):
            if field not in check:
                print(
                    f'Error: Check at index {i} is missing required field "{field}".',
                    file=sys.stderr,
                )
                sys.exit(2)

        if check["category"] not in VALID_CATEGORIES:
            print(
                f'Error: Check at index {i} has invalid category "{check["category"]}". '
                f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}",
                file=sys.stderr,
            )
            sys.exit(2)

        if check["status"] not in VALID_STATUSES:
            print(
                f'Error: Check at index {i} has invalid status "{check["status"]}". '
                f"Valid statuses: {', '.join(sorted(VALID_STATUSES))}",
                file=sys.stderr,
            )
            sys.exit(2)

    return checks


def group_by_category(checks: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group checks by category, preserving the defined display order."""
    grouped: dict[str, list[dict[str, str]]] = {}
    for cat in CATEGORY_ORDER:
        items = [c for c in checks if c["category"] == cat]
        if items:
            grouped[cat] = items
    return grouped


def compute_summary(checks: list[dict[str, str]]) -> dict[str, int]:
    """Compute summary counts across all checks."""
    return {
        "total": len(checks),
        "pass": sum(1 for c in checks if c["status"] == "pass"),
        "fail": sum(1 for c in checks if c["status"] == "fail"),
        "warning": sum(1 for c in checks if c["status"] == "warning"),
    }


def generate_report(checks: list[dict[str, str]]) -> str:
    """Generate the full Markdown prerequisite validation report."""
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = compute_summary(checks)
    grouped = group_by_category(checks)
    has_failures = summary["fail"] > 0

    # Title
    lines.append("# Prerequisite Validation Report")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append("")

    # Executive summary
    lines.append("## Summary")
    lines.append("")
    if not has_failures and summary["warning"] == 0:
        lines.append(
            "All prerequisite checks passed. The tenant is ready to proceed "
            "with POC configuration."
        )
    elif not has_failures:
        lines.append(
            f'{summary["pass"]} of {summary["total"]} checks passed with '
            f'{summary["warning"]} warning(s). Review warnings before proceeding.'
        )
    else:
        lines.append(
            f'**{summary["fail"]} of {summary["total"]} checks failed.** '
            "Resolve the failures below before proceeding with POC configuration."
        )
    lines.append("")

    # Summary table
    lines.append("| Result  | Count |")
    lines.append("|---------|-------|")
    lines.append(f'| PASS    | {summary["pass"]}     |')
    lines.append(f'| FAIL    | {summary["fail"]}     |')
    lines.append(f'| WARNING | {summary["warning"]}     |')
    lines.append(f'| **Total** | **{summary["total"]}** |')
    lines.append("")

    # Detailed results by category
    lines.append("## Detailed Results")
    lines.append("")

    for category, items in grouped.items():
        label = CATEGORY_LABELS.get(category, category.title())
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Status | Check | Required | Current |")
        lines.append("|--------|-------|----------|---------|")

        for item in items:
            icon = STATUS_ICONS[item["status"]]
            name = item["name"]
            required = item["required"]
            current = item["current"]
            lines.append(f"| {icon} | {name} | {required} | {current} |")
        lines.append("")

        # Per-category failures and remediation
        failures = [c for c in items if c["status"] == "fail"]
        warnings = [c for c in items if c["status"] == "warning"]

        if failures:
            lines.append(f"> [!IMPORTANT]")
            lines.append(f"> **{len(failures)} failed check(s) in {label}:**")
            for f in failures:
                lines.append(f'> - **{f["name"]}**: Required `{f["required"]}`, found `{f["current"]}`')
            lines.append(">")
            lines.append(f"> {REMEDIATION_HINTS.get(category, 'Review the requirement documentation.')}")
            lines.append("")

        if warnings:
            lines.append(f"> [!WARNING]")
            lines.append(f"> **{len(warnings)} warning(s) in {label}:**")
            for w in warnings:
                lines.append(f'> - **{w["name"]}**: Required `{w["required"]}`, found `{w["current"]}`')
            lines.append("")

    # Remediation section (only if there are failures)
    if has_failures:
        lines.append("## Remediation Steps")
        lines.append("")
        lines.append(
            "Address the following items in order before proceeding with the POC:"
        )
        lines.append("")

        step = 1
        for category in CATEGORY_ORDER:
            items = grouped.get(category, [])
            failures = [c for c in items if c["status"] == "fail"]
            if not failures:
                continue
            label = CATEGORY_LABELS.get(category, category.title())
            lines.append(f"{step}. **{label}**")
            for f in failures:
                lines.append(
                    f'   - Resolve **{f["name"]}**: ensure `{f["required"]}` is satisfied '
                    f'(currently `{f["current"]}`)'
                )
            step += 1
        lines.append("")
        lines.append(
            "After remediation, re-run prerequisite validation to confirm readiness."
        )
        lines.append("")

    # Next steps
    lines.append("## Next Steps")
    lines.append("")
    if not has_failures:
        lines.append(
            "Prerequisites are satisfied. Proceed to **Phase 3: Configuration**."
        )
    else:
        lines.append(
            "1. Complete the remediation steps listed above\n"
            "2. Re-validate prerequisites\n"
            "3. Once all checks pass, proceed to **Phase 3: Configuration**"
        )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Entry point."""
    args = parse_args()

    # Load and validate
    data = load_input(args.input)
    checks = validate_input(data)

    # Generate report
    report = generate_report(checks)

    # Output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    # Exit code: 1 if any failures
    has_failures = any(c["status"] == "fail" for c in checks)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
