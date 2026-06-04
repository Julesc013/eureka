# Hard Query Eval 00

Task ID: `HARD-QUERY-EVAL-00`

Status: `PASS`.

This package records the first runnable hard-query usefulness eval over the current resolver/surface/rendering stack.

## What This Task Adds

- deterministic hard-query registry
- expected answer-shape rules
- scorecard dimensions and pass gates
- synthetic fixture resolution-run outputs
- SurfaceKernel and baseline-renderer coverage checks
- public action-policy and truth-boundary tests

## What This Task Does Not Do

This task does not seed a corpus, add reviewed records, call live sources, promote candidates, rewire gateway routes, or launch public routes.

## Runtime/Eval Artifacts

```text
evals/hard_queries/**
tests/evals/test_hard_query_eval.py
tests/runtime/test_surface_hard_query_eval.py
```

## Next Task

Recommended next task: `REVIEWED-SEED-CORPUS-00`.
