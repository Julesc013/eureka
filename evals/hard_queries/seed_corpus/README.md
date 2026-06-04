# Hard Query Seed Corpus

This package maps the six `HARD-QUERY-EVAL-00` queries into seed-corpus
readiness states.

The fixtures are public-alpha readiness material, not reviewed truth.

## Files

- `seed_corpus.v0.json`: seed item records for the six hard queries.
- `query_seed_map.v0.json`: per-query readiness, counts, and gaps.
- `review_backlog.v0.json`: review/manual-observation backlog.
- `public_alpha_corpus_readiness.v0.json`: alpha corpus gate report.
- `seed_corpus_schema_notes.md`: model rules and JSON choice.
- `loader.py`: stdlib-only loader/validator and SurfaceKernel projection helper.

The fixture files use JSON so the eval lane remains stdlib-only and consistent
with the current hard-query assets.

## Gate Result

The current seed package is intentionally marked:

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```

The six hard queries are mapped, but this task does not create reviewed truth.
Every seed item carries explicit false flags for accepted truth, reviewed
material, live source calls, and reviewed/public/master index mutation.
