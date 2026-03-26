# entra-poc-advisor Benchmark Suite

Automated benchmark suite for measuring the impact of the `entra-poc-advisor` Claude Skill on Entra POC task quality. Runs test cases with and without the skill enabled and compares results across triggering accuracy, functional completeness, safety compliance, and output format adherence.

## Prerequisites

- Python 3.10+
- `anthropic` Python package (for API mode): `pip install anthropic`
- `ANTHROPIC_API_KEY` environment variable set (for API mode)

## Quick Start

```bash
# Run with skill enabled
python run_benchmark.py --with-skill -o results/with-skill.json

# Run without skill enabled
python run_benchmark.py --without-skill -o results/without-skill.json

# Compare results
python compare_results.py results/with-skill.json results/without-skill.json -o results/comparison-report.md
```

## Test Categories

### Triggering Tests (`test_cases/triggering.json`)

15 test cases that verify the skill activates on relevant queries and stays silent on unrelated ones. Each test has an `expected_trigger` field (true/false). Evaluated by keyword pattern matching against skill-specific vocabulary.

### Functional Tests (`test_cases/functional.json`)

10 test cases that evaluate response quality for core skill tasks: POC planning, configuration review, gap analysis, documentation generation, and PowerShell script generation. Each test defines `expected_elements` that should appear in the response. Also evaluated for safety compliance.

### Performance Tests (`test_cases/performance.json`)

5 end-to-end test cases that measure output format compliance and safety for complex, multi-step queries. Evaluated for adherence to documentation standards, PowerShell conventions, and gap report structure.

## Execution Modes

### API Mode (Automated)

Sends prompts to the Anthropic Messages API. Uses `--with-skill` or `--without-skill` flags to control whether the SKILL.md content is injected as a system prompt.

```bash
python run_benchmark.py --with-skill --categories triggering functional -o results/with-skill.json
python run_benchmark.py --without-skill --categories triggering functional -o results/without-skill.json
```

Options:
- `--categories`: Limit to specific test categories (default: all)
- `--model`: Override the Claude model (default: `claude-sonnet-4-20250514`)

### Manual Mode

Displays each test query and prompts you to paste Claude's response. Useful for testing via Claude.ai with the skill installed in a Project.

```bash
python run_benchmark.py --manual -o results/manual-results.json
```

## Evaluators

| Module | What It Checks |
|---|---|
| `evaluators/triggering.py` | Whether the response contains skill-specific patterns matching the expected trigger state |
| `evaluators/functional.py` | Presence of expected elements, structural completeness, and per-criteria scoring |
| `evaluators/safety.py` | Absence of destructive operations (Remove-*, DELETE, production-scope changes, credential exposure) |
| `evaluators/format_compliance.py` | Adherence to documentation, PowerShell, and gap report templates defined in the skill |

## Scoring Rubrics

`scoring/rubrics.json` defines 6 rubrics for qualitative assessment:

1. **Structural Completeness** - Required sections and organization
2. **Safety Compliance** - Absence of dangerous operations
3. **Technical Accuracy** - Correct Entra concepts, APIs, and cmdlets
4. **Output Consistency** - Reproducibility across runs
5. **Format Compliance** - Adherence to template standards
6. **Triggering Accuracy** - Correct activation/suppression

## Comparing Results

After running both with-skill and without-skill benchmarks:

```bash
python compare_results.py results/with-skill.json results/without-skill.json -o results/comparison-report.md
```

The comparison report includes:
- Executive summary with improvement metrics per category
- Detailed per-test results table
- Expected vs actual performance against SPECv2 Section 9.6 targets

### Expected Results (from SPECv2 Section 9.6)

| Metric | Without Skill | With Skill |
|---|---|---|
| Structural completeness | 40-60% | 85-95% |
| Safety compliance | 70-80% | 95-100% |
| Entra technical accuracy | 50-70% | 80-90% |
| Output consistency | 30-50% | 75-90% |
| Format compliance | 20-40% | 85-95% |

## File Structure

```
benchmarks/
  README.md                   # This file
  run_benchmark.py            # Main benchmark runner
  compare_results.py          # Results comparison and reporting
  evaluators/
    __init__.py
    triggering.py             # Triggering evaluation logic
    functional.py             # Functional evaluation logic
    safety.py                 # Safety compliance evaluation
    format_compliance.py      # Output format evaluation
  test_cases/
    triggering.json           # 15 triggering test definitions
    functional.json           # 10 functional test definitions
    performance.json          # 5 performance comparison definitions
  scoring/
    rubrics.json              # 6 scoring rubrics
  results/                    # Generated results (gitignored)
    .gitkeep
```
