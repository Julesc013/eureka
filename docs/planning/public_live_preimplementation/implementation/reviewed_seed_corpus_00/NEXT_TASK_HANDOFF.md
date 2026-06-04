# Next Task Handoff

Task ID: `REVIEWED-SEED-CORPUS-00`

Recommended next task:

```text
MANUAL-OBSERVATION-BATCH-00
```

## Why

The seed-corpus readiness layer now maps all six required hard queries, but it
does not contain review-event-backed verified seed records. The next useful
work is manual observation and review-ready evidence collection, not public
alpha readiness.

## Inputs For Next Task

```text
evals/hard_queries/seed_corpus/seed_corpus.v0.json
evals/hard_queries/seed_corpus/query_seed_map.v0.json
evals/hard_queries/seed_corpus/review_backlog.v0.json
evals/hard_queries/seed_corpus/public_alpha_corpus_readiness.v0.json
docs/planning/public_live_preimplementation/implementation/reviewed_seed_corpus_00/
```

## Constraints To Preserve

```text
reviewed records require review events
manual observations are support, not truth by themselves
candidates do not self-promote
needs are not absences
near_miss is not verified
fallback output is not reviewed truth
public surfaces stay read-only
no live source fanout without explicit future gates
```
