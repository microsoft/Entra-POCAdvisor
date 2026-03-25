"""Check output format compliance with documentation and PowerShell standards.

Validates that model responses conform to the formatting rules defined in
the entra-poc-advisor specification (SPEC §8 Documentation Standards,
§9 PowerShell Standards, §4.3 Gap Report format).
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

# ── Per-type check definitions ────────────────────────────────────────

_DOCUMENTATION_CHECKS: dict[str, str | None] = {
    "markdown_headers": r"(?m)^#{1,6}\s+\S",
    "numbered_steps": r"(?m)^\s*\d+\.\s+",
    "mermaid_diagram": r"```mermaid",
    "callouts": r">\s*\[!(NOTE|WARNING|IMPORTANT|CAUTION|TIP)\]",
    "tables": r"\|.*\|.*\|",
    "prerequisites_section": r"(?i)(?:^|\n)#{1,6}\s+.*prerequisite",
}

_POWERSHELL_CHECKS: dict[str, str | None] = {
    "connect_mggraph": r"(?i)Connect-MgGraph",
    "invoke_mggraphrequest": r"(?i)Invoke-MgGraphRequest",
    "shouldprocess": r"(?i)ShouldProcess",
    "whatif": r"(?i)-WhatIf|WhatIfPreference",
    "error_handling": r"(?i)\btry\s*\{|catch\s*\{",
    "color_coded_writehost": (
        r"(?i)Write-Host\s+.+-ForegroundColor\s+"
        r"(?:Cyan|Green|Yellow|Red)"
    ),
    "no_remove_cmdlet": None,  # special: absence check
}

_GAP_REPORT_CHECKS: dict[str, str | None] = {
    "executive_summary": r"(?i)(?:^|\n)#{1,6}\s+.*(?:executive\s+summary|summary)",
    "status_table": r"\|.*(?:Configured|Missing|Partially).*\|",
    "current_vs_expected": r"(?i)(?:current|existing).{0,40}(?:expected|target|required)",
    "remediation_steps": r"(?i)(?:remediat|action\s+item|next\s+step|recommendation)",
    "mermaid_diagram": r"```mermaid",
}


def _run_checks(
    response: str,
    check_defs: dict[str, str | None],
    output_type: str,
) -> tuple[dict[str, bool], list[str]]:
    """Run regex-based checks and return (checks_dict, details_list)."""
    checks: dict[str, bool] = {}
    details: list[str] = []

    for name, pattern in check_defs.items():
        if name == "no_remove_cmdlet":
            # Special absence check: Remove-* cmdlets must NOT be present
            # outside a negation context.
            has_remove = bool(
                re.search(r"\bRemove-\w+", response, flags=re.IGNORECASE)
            )
            if has_remove:
                # Allow if only mentioned in negation context
                negated = all(
                    _is_negated(response, m)
                    for m in re.finditer(
                        r"\bRemove-\w+", response, flags=re.IGNORECASE
                    )
                )
                passed = negated
            else:
                passed = True
            checks[name] = passed
            details.append(
                f"[{output_type}] {name}: "
                + ("PASS – no destructive cmdlet" if passed else "FAIL – Remove-* cmdlet found")
            )
            continue

        if pattern is None:
            continue

        found = bool(re.search(pattern, response))
        checks[name] = found
        details.append(
            f"[{output_type}] {name}: " + ("PASS" if found else "FAIL")
        )

    return checks, details


def _is_negated(text: str, match: re.Match[str], radius: int = 120) -> bool:
    """Return True if the match sits in a negation context."""
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    ctx = text[start:end].lower()
    negations = [
        "never",
        "do not",
        "don't",
        "must not",
        "will not",
        "won't",
        "should not",
        "shouldn't",
        "avoid",
        "not include",
        "no delete",
        "not remove",
        "blocked",
        "prohibited",
    ]
    return any(n in ctx for n in negations)


def evaluate(response: str, output_type: str) -> dict:
    """Score format compliance for a given output type.

    Parameters
    ----------
    response:
        The full model response text.
    output_type:
        One of ``"documentation"``, ``"powershell"``, or ``"gap_report"``.

    Returns
    -------
    dict
        ``score``       – 0.0-1.0 fraction of checks passed.
        ``checks``      – dict mapping check names to bool results.
        ``output_type`` – the type that was evaluated.
        ``details``     – list of human-readable detail strings.
    """

    output_type_lower = output_type.lower().strip()

    if output_type_lower == "documentation":
        check_defs = _DOCUMENTATION_CHECKS
    elif output_type_lower == "powershell":
        check_defs = _POWERSHELL_CHECKS
    elif output_type_lower in ("gap_report", "gap-report", "gapreport"):
        check_defs = _GAP_REPORT_CHECKS
        output_type_lower = "gap_report"
    else:
        return {
            "score": 0.0,
            "checks": {},
            "output_type": output_type,
            "details": [
                f"Unknown output_type '{output_type}'. "
                "Expected 'documentation', 'powershell', or 'gap_report'."
            ],
        }

    checks, details = _run_checks(response, check_defs, output_type_lower)

    total = len(checks)
    passed_count = sum(1 for v in checks.values() if v)
    score = passed_count / total if total > 0 else 1.0

    return {
        "score": round(score, 4),
        "checks": checks,
        "output_type": output_type_lower,
        "details": details,
    }


# ── CLI entry-point ──────────────────────────────────────────────────
if __name__ == "__main__":
    # Usage:
    #   echo "<response text>" | python format_compliance.py <output_type>
    #
    # Where <output_type> is one of: documentation, powershell, gap_report

    if len(sys.argv) < 2:
        print(
            "Usage: echo '<response>' | python format_compliance.py "
            "<documentation|powershell|gap_report>",
            file=sys.stderr,
        )
        sys.exit(1)

    otype = sys.argv[1]
    response_text = sys.stdin.read()
    result = evaluate(response_text, otype)
    print(json.dumps(result, indent=2))
