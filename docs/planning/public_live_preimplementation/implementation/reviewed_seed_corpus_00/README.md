# Reviewed Seed Corpus 00

Task ID: `REVIEWED-SEED-CORPUS-00`

Status: `PASS_WITH_WARNINGS`.

This package turns the hard-query eval layer into a concrete seed-corpus
readiness layer. It adds deterministic seed items, per-query readiness maps,
review backlog material, public-alpha corpus gate data, focused tests, and this
implementation report package.

The package does not create reviewed records, review events, source calls,
source observations, or index mutations. Candidate, need, near_miss,
policy_blocked, and unavailable states remain non-truth states.

## Key Files

```text
evals/hard_queries/seed_corpus/
tests/evals/test_reviewed_seed_corpus.py
tests/runtime/test_surface_seed_corpus_projection.py
docs/planning/public_live_preimplementation/implementation/reviewed_seed_corpus_00/
```

## Gate Result

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```

The six required hard queries are mapped, but the package contains zero
review-event-backed verified seed records. The recommended next task is
`MANUAL-OBSERVATION-BATCH-00`.
