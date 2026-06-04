# Implementation Report

Task ID: `HARD-QUERY-EVAL-00`

Status: `PASS`.

## Files Changed

Eval assets:

```text
evals/README.md
evals/hard_queries/README.md
evals/hard_queries/__init__.py
evals/hard_queries/evaluator.py
evals/hard_queries/expected_answer_shapes_v0.json
evals/hard_queries/fixtures_v0.py
evals/hard_queries/hard_query_set_v0.json
evals/hard_queries/usefulness_scorecard_v0.json
```

Tests:

```text
tests/evals/test_hard_query_eval.py
tests/runtime/test_surface_hard_query_eval.py
```

Reports:

```text
docs/planning/public_live_preimplementation/implementation/hard_query_eval_00/
```

Generated operating context:

```text
.aide/context/latest-task-packet.md
```

## Behavior Added

The hard-query eval can load six required hard queries, validate expected answer shapes and scorecard gates, construct deterministic synthetic resolution-run fixtures, project those fixtures through SurfaceKernel, render them through all baseline profiles, and compute deterministic usefulness scores.

## Boundary Decision

The implementation lives in `evals/hard_queries/**` rather than product runtime behavior. It imports the current SurfaceKernel and renderer stack for evaluation, but it does not change gateway routes, source providers, review stores, or indexes.

## Non-Behavior

No live web/API/source calls were added.

No reviewed records were added.

No candidate promotion path was added.

No public route rewiring was added.

No reviewed, public, or master index mutation was added.
