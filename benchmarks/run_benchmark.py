#!/usr/bin/env python3
"""
Benchmark runner for entra-poc-advisor skill.

Runs test cases with and without the skill enabled, collecting results
for comparison. Supports Claude API for automated execution and manual
mode for Claude.ai testing.

Usage:
    python run_benchmark.py --with-skill --output results/with-skill.json
    python run_benchmark.py --without-skill --output results/without-skill.json
    python run_benchmark.py --manual --output results/manual-results.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for evaluator imports
sys.path.insert(0, str(Path(__file__).parent))

from evaluators import triggering as eval_triggering
from evaluators import functional as eval_functional
from evaluators import safety as eval_safety
from evaluators import format_compliance as eval_format


def load_test_cases(category: str) -> list[dict]:
    """Load test cases from JSON file."""
    test_dir = Path(__file__).parent / "test_cases"
    filepath = test_dir / f"{category}.json"
    if not filepath.exists():
        print(f"ERROR: Test case file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_rubrics() -> dict:
    """Load scoring rubrics."""
    rubrics_path = Path(__file__).parent / "scoring" / "rubrics.json"
    if not rubrics_path.exists():
        return {}
    with open(rubrics_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_api_test(test_case: dict, skill_enabled: bool, model: str) -> dict:
    """Run a single test case via the Anthropic API."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": test_case["query"]}]

    kwargs = {
        "model": model,
        "max_tokens": 8192,
        "messages": messages,
    }

    # Configure skill if enabled
    # Note: The exact API parameter for skills may vary.
    # Update this when the skills API is finalized.
    if skill_enabled:
        # Placeholder for skill configuration
        # kwargs["container"] = {"skills": ["entra-poc-advisor"]}
        kwargs["system"] = _load_skill_as_system_prompt()

    start_time = time.time()
    response = client.messages.create(**kwargs)
    elapsed = time.time() - start_time

    return {
        "test_id": test_case["id"],
        "category": test_case["category"],
        "query": test_case["query"],
        "skill_enabled": skill_enabled,
        "response": response.content[0].text,
        "tokens_input": response.usage.input_tokens,
        "tokens_output": response.usage.output_tokens,
        "elapsed_seconds": round(elapsed, 2),
        "stop_reason": response.stop_reason,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _load_skill_as_system_prompt() -> str:
    """Load SKILL.md content as a system prompt for API testing."""
    skill_path = Path(__file__).parent.parent / ".github" / "skills" / "entra-poc-advisor" / "SKILL.md"
    if not skill_path.exists():
        print(f"WARNING: SKILL.md not found at {skill_path}", file=sys.stderr)
        return ""
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Strip YAML frontmatter for system prompt use
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()
    return content


def run_manual_test(test_case: dict) -> dict:
    """Run a single test case in manual mode (prompt user for response)."""
    print(f"\n{'='*60}")
    print(f"Test: {test_case['id']} - {test_case.get('description', '')}")
    print(f"{'='*60}")
    print(f"\nQuery to send to Claude:\n")
    print(f"  {test_case['query']}")
    print(f"\nPaste Claude's response below (enter blank line + 'END' to finish):")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    response = "\n".join(lines)

    return {
        "test_id": test_case["id"],
        "category": test_case["category"],
        "query": test_case["query"],
        "skill_enabled": None,  # Manual mode - user manages this
        "response": response,
        "tokens_input": None,
        "tokens_output": None,
        "elapsed_seconds": None,
        "stop_reason": "manual",
        "model": "manual",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_result(result: dict, test_case: dict) -> dict:
    """Evaluate a single test result using appropriate evaluators."""
    evaluations = {}
    category = test_case["category"]

    if category == "triggering":
        evaluations["triggering"] = eval_triggering.evaluate(
            result["response"], test_case["expected_trigger"]
        )

    elif category == "functional":
        evaluations["functional"] = eval_functional.evaluate(
            result["response"], test_case
        )
        evaluations["safety"] = eval_safety.evaluate(result["response"])

    elif category == "performance":
        evaluations["safety"] = eval_safety.evaluate(result["response"])

        # Determine output type for format evaluation
        output_type = "documentation"
        if "powershell" in test_case.get("query", "").lower():
            output_type = "powershell"
        elif "gap" in test_case.get("query", "").lower():
            output_type = "gap_report"

        evaluations["format_compliance"] = eval_format.evaluate(
            result["response"], output_type
        )

    return evaluations


def run_benchmark(
    categories: list[str],
    skill_enabled: bool | None,
    mode: str,
    model: str,
) -> list[dict]:
    """Run all test cases in specified categories."""
    results = []

    for category in categories:
        test_cases = load_test_cases(category)
        print(f"\nRunning {len(test_cases)} {category} tests...")

        for i, test_case in enumerate(test_cases, 1):
            test_id = test_case["id"]
            print(f"  [{i}/{len(test_cases)}] {test_id}: {test_case.get('description', '')[:50]}...")

            if mode == "api":
                result = run_api_test(test_case, bool(skill_enabled), model)
            else:
                result = run_manual_test(test_case)

            # Evaluate
            evaluations = evaluate_result(result, test_case)
            result["evaluations"] = evaluations

            results.append(result)

            # Rate limit buffer for API mode
            if mode == "api":
                time.sleep(1)

    return results


def print_summary(results: list[dict]) -> None:
    """Print a summary of benchmark results."""
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")

    # Group by category
    by_category: dict[str, list] = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r)

    for category, cat_results in by_category.items():
        print(f"\n{category.upper()} ({len(cat_results)} tests)")
        print("-" * 40)

        if category == "triggering":
            correct = sum(
                1 for r in cat_results
                if r.get("evaluations", {}).get("triggering", {}).get("correct", False)
            )
            total = len(cat_results)
            print(f"  Accuracy: {correct}/{total} ({100*correct/total:.0f}%)")

        elif category == "functional":
            scores = [
                r.get("evaluations", {}).get("functional", {}).get("score", 0)
                for r in cat_results
            ]
            avg = sum(scores) / len(scores) if scores else 0
            print(f"  Average score: {avg:.1%}")

            safe = sum(
                1 for r in cat_results
                if r.get("evaluations", {}).get("safety", {}).get("safe", True)
            )
            print(f"  Safety compliance: {safe}/{len(cat_results)}")

        elif category == "performance":
            for r in cat_results:
                fmt = r.get("evaluations", {}).get("format_compliance", {})
                safety = r.get("evaluations", {}).get("safety", {})
                print(f"  {r['test_id']}: format={fmt.get('score', 0):.1%} safety={'PASS' if safety.get('safe', True) else 'FAIL'}")


def main():
    parser = argparse.ArgumentParser(
        description="Run entra-poc-advisor benchmark suite"
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--with-skill", action="store_true",
        help="Run with skill enabled (API mode)"
    )
    mode_group.add_argument(
        "--without-skill", action="store_true",
        help="Run without skill enabled (API mode)"
    )
    mode_group.add_argument(
        "--manual", action="store_true",
        help="Manual mode (paste responses interactively)"
    )

    parser.add_argument(
        "--output", "-o", type=str, required=True,
        help="Output file path for results JSON"
    )
    parser.add_argument(
        "--categories", nargs="+",
        choices=["triggering", "functional", "performance"],
        default=["triggering", "functional", "performance"],
        help="Test categories to run (default: all)"
    )
    parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-20250514",
        help="Model to use for API mode"
    )

    args = parser.parse_args()

    skill_enabled = args.with_skill if not args.manual else None
    mode = "manual" if args.manual else "api"

    print(f"Benchmark Configuration:")
    print(f"  Mode: {mode}")
    print(f"  Skill: {'enabled' if skill_enabled else 'disabled' if skill_enabled is not None else 'manual'}")
    print(f"  Categories: {', '.join(args.categories)}")
    print(f"  Model: {args.model}")
    print(f"  Output: {args.output}")

    # Run benchmark
    results = run_benchmark(args.categories, skill_enabled, mode, args.model)

    # Print summary
    print_summary(results)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "skill_enabled": skill_enabled,
            "model": args.model,
            "categories": args.categories,
            "total_tests": len(results),
        },
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
