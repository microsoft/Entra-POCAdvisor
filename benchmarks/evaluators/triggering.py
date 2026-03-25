"""Evaluate whether the entra-poc-advisor skill triggered correctly.

Analyzes Claude's response for skill-specific patterns that indicate the
entra-poc-advisor skill was activated (or correctly not activated) based
on the input prompt.
"""

from __future__ import annotations

import json
import re
import sys

# Patterns whose presence signals the skill triggered and produced
# domain-specific Entra POC content rather than a generic response.
POSITIVE_PATTERNS: list[str] = [
    "operation mode",
    "POC lifecycle",
    "Entra Suite",
    "prerequisites",
    "gap analysis",
    "audit trail",
    "pilot group",
    "scenario",
    "traffic forwarding",
    "connector",
]


def evaluate(response: str, expected_trigger: bool) -> dict:
    """Determine whether the skill triggered as expected.

    Parameters
    ----------
    response:
        The full text of the model's response.
    expected_trigger:
        ``True`` if the skill *should* have triggered for this prompt,
        ``False`` if it should *not* have triggered (e.g. an off-topic
        query that should receive a generic answer).

    Returns
    -------
    dict
        ``correct``           – whether the actual trigger matched the expected value.
        ``triggered``         – whether the skill appears to have triggered.
        ``expected``          – the ``expected_trigger`` value passed in.
        ``confidence``        – 0.0-1.0 indicating how confident we are in the
                                 trigger detection (based on pattern density).
        ``matched_patterns``  – list of positive-pattern strings found.
    """

    response_lower = response.lower()

    matched_patterns: list[str] = [
        pattern
        for pattern in POSITIVE_PATTERNS
        if pattern.lower() in response_lower
    ]

    # A response is considered "triggered" when it contains at least two
    # distinct skill-specific patterns.  A single match could be
    # coincidental; two or more is a strong signal.
    match_count = len(matched_patterns)
    triggered = match_count >= 2

    # Confidence is proportional to how many patterns matched, capped at
    # 1.0.  Each pattern beyond the threshold adds 0.1 confidence.
    if match_count == 0:
        confidence = 1.0 if not expected_trigger else 0.0
    elif match_count == 1:
        confidence = 0.4
    else:
        confidence = min(1.0, 0.5 + (match_count - 2) * 0.1)

    # If the trigger detection doesn't match the expectation, invert the
    # confidence score so it reflects certainty about *incorrectness*.
    correct = triggered == expected_trigger
    if not correct:
        confidence = 1.0 - confidence

    return {
        "correct": correct,
        "triggered": triggered,
        "expected": expected_trigger,
        "confidence": round(confidence, 2),
        "matched_patterns": matched_patterns,
    }


# ── CLI entry-point ──────────────────────────────────────────────────
if __name__ == "__main__":
    # Usage:
    #   echo "<response text>" | python triggering.py [--expected-trigger | --no-trigger]
    #
    # By default, the script assumes the skill *should* have triggered.

    expected: bool = True
    if "--no-trigger" in sys.argv:
        expected = False
    elif "--expected-trigger" in sys.argv:
        expected = True

    response_text = sys.stdin.read()
    result = evaluate(response_text, expected)
    print(json.dumps(result, indent=2))
