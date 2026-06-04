# Next Task Handoff

Task ID: `HARD-QUERY-EVAL-00`

Recommended next task:

```text
REVIEWED-SEED-CORPUS-00
```

## Why

The hard-query eval now defines messy public-alpha query pressure, expected answer shapes, score dimensions, public renderer coverage, and truth-boundary checks.

The next task should use this framework to define and build enough reviewed/candidate/need material for public alpha without overstating coverage.

## Inputs For Next Task

```text
evals/hard_queries/hard_query_set_v0.json
evals/hard_queries/expected_answer_shapes_v0.json
evals/hard_queries/usefulness_scorecard_v0.json
evals/hard_queries/fixtures_v0.py
docs/planning/public_live_preimplementation/implementation/hard_query_eval_00/
```

## Constraints To Preserve

```text
review remains the truth boundary
fixtures are not evidence
candidates are not reviewed records
needs are not absences
public output remains read-only
no live source fanout without explicit future gates
no corpus coverage claim without reviewed support
```
