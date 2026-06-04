# Implementation Report

Task ID: `REVIEWED-SEED-CORPUS-00`

Status: `PASS_WITH_WARNINGS`.

## Behavior Added

Added a deterministic hard-query seed-corpus package under:

```text
evals/hard_queries/seed_corpus/
```

The package includes:

```text
seed_corpus.v0.json
query_seed_map.v0.json
review_backlog.v0.json
public_alpha_corpus_readiness.v0.json
seed_corpus_schema_notes.md
loader.py
```

The loader validates seed records, query maps, review backlog entries, and the
public-alpha readiness gate. It also projects seed items through the current
`SurfaceKernel` and baseline renderers.

## Non-Behavior

No reviewed records were created.

No review events were created.

No source providers were called.

No source observations were generated.

No reviewed, public, or master indexes were mutated.

No public route or gateway behavior was changed.

## Public Projection

Seed items project as resolver-run fallback summaries through SurfaceKernel.
Public projections strip operator-only actions and retain honest status:
candidate, need, near_miss, policy_blocked, and unavailable.

## Warning

The task implementation passes, but the corpus gate fails honestly:

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```
