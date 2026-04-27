# Changes Made

Runtime/eval changes:

- Archive Resolution Eval Runner v0 now emits `result_shape.primary_candidate`
  checks.
- `lanes.expected_lanes` is now evaluated against current bounded result lanes.
- `ranking.bad_result_patterns` is now evaluated as deterministic bad-result
  avoidance, not production ranking.
- Satisfied hard tasks require strict source-backed search evidence, result
  shape, expected lane fit, and bad-result avoidance.

Tests:

- Added `tests/evals/test_old_platform_result_refinement.py`.
- Updated hardening so satisfied archive hard evals must include source-backed
  search evidence plus satisfied result-shape, lane, and bad-result checks.
- Updated historical Hard Eval Satisfaction Pack validation to allow later
  source-backed refinement from partial to satisfied.

No fixture payloads were added or changed.

No live crawling, scraping, live source calls, arbitrary local ingestion,
fuzzy/vector/LLM retrieval, Rust behavior ports, native app projects, or
deployment infrastructure were added.
