# Hard Eval Satisfaction Pack v0

Hard Eval Satisfaction Pack v0 records the targeted archive-resolution eval
follow-up after Search Usefulness Audit Delta v1.

This pack is eval/reporting plus bounded runner evidence mapping. It does not
weaken hard evals, remove tasks, fabricate source evidence, add live sources,
scrape external systems, add fuzzy/vector/LLM retrieval, port Rust behavior,
start native app work, add deployment infrastructure, or claim production
readiness.

## Baseline

The baseline was the live pre-change archive-resolution eval posture recorded by
Search Usefulness Audit Delta v1:

| status | count |
| --- | ---: |
| capability_gap | 1 |
| not_satisfied | 5 |

## Current Result

After this pack, the live archive-resolution eval runner reports:

| status | count |
| --- | ---: |
| capability_gap | 1 |
| partial | 5 |

The five moved tasks are partial, not satisfied. They have source-backed local
candidates, but lane placement and bad-result pattern scoring remain explicitly
not evaluable in Eval Runner v0.

## Files

- `CURRENT_FAILURES.md`: baseline failure shape.
- `TASK_BY_TASK_ANALYSIS.md`: current task-level evidence and remaining gaps.
- `SATISFACTION_PLAN.md`: target scope and guardrails.
- `CHANGES_MADE.md`: implementation and docs changes.
- `REMAINING_GAPS.md`: work intentionally left open.
- `hard_eval_satisfaction_report.json`: stable machine-readable summary.

## How To Verify

Run:

```bash
python -m unittest discover -s tests/evals -t .
python -m unittest tests.hardening.test_eval_hardness_guards
python scripts/run_archive_resolution_evals.py --json
```

Expected archive-resolution status counts are `capability_gap=1` and
`partial=5`.
