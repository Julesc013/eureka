# Hard Queries

`evals/hard_queries/` contains the first deterministic hard-query usefulness
eval over the SurfaceKernel and baseline renderers.

This eval is fixture-only. It does not call live sources, record evidence,
promote reviewed records, mutate indexes, or launch public routes.

## Contents

- `hard_query_set_v0.json`: six required messy real query definitions.
- `expected_answer_shapes_v0.json`: useful answer-shape rules per query.
- `usefulness_scorecard_v0.json`: deterministic score dimensions and pass gates.
- `fixtures_v0.py`: synthetic resolution-run fixture cases.
- `evaluator.py`: stdlib-only loader, validator, renderer coverage, and scoring helpers.

## Fixture Disclaimer

Synthetic hard-query fixtures are evaluation pressure only.

They are not evidence.

They are not reviewed records.

They do not promote corpus truth.
