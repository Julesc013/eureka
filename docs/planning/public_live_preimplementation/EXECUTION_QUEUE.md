# Execution Queue

This queue preserves the mega-prompt dependency order but reconciles it with
current repo authority.

## Current Repair Queue

The original public-live implementation queue has advanced. Current posture:

1. `INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT` through `REVIEWED-CORPUS-SEED-BATCH-02`: completed or consolidated.
2. `SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01`: completed with external full-discovery handoff.
3. `SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-01`: completed; external discovery was current and red.
4. `ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01`: completed for the focused architecture-boundary labels.
5. `QUEUE-HANDOFF-DRIFT-REPAIR-01`: current repair task.

After this repair, remaining residual families should drive the next task:

```text
SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01
GENERATED-ARTIFACT-DRIFT-REPAIR-01
CONTRACT-SCHEMA-DRIFT-REPAIR-01
SOURCE-SNAPSHOT-FAILURE-REPAIR-01
```

## Reconciled Mega Queue

`AUTHORITY-LOCK-00`: satisfied for this package; rerun before product edits.

`PUBLIC-SCOPE-V1-00`: partially satisfied by current docs; keep read-only,
bounded, no public fanout, no public mutation.

`SEMANTIC-CORE-CONTRACTS-00`: mostly satisfied by TSIS-00; run only as a gap
audit unless existing contracts fail fallback needs.

`RESOLVER-SPINE-00`: partially satisfied by existing runtime paths; use as an
alignment task, not a greenfield rewrite.

`INDEXLESS-LIVE-SEARCH-FALLBACK-00`: completed as governed fallback behind the
engine run seam.

`REVIEW-LEDGER-00`: completed as the review/audit truth boundary for
candidates and needs.

`WORKBENCH-RUN-REVIEW-PROJECTION-00`: completed as the private/operator
projection over runs, fallback output, review items, ledger decisions, and
audit events.

`SURFACE-KERNEL-00` and `BASELINE-RENDERERS-00`: completed as projection and
baseline representation layers over policy-filtered view models.

`HARD-QUERY-EVAL-00` and `REVIEWED-SEED-CORPUS-00`: completed as evaluation and
seed-corpus readiness layers. Corpus work remains below public-alpha threshold
after `REVIEWED-CORPUS-SEED-BATCH-02`.

`PUBLIC-ALPHA-READINESS-00` and `PUBLIC-ALPHA-LAUNCH-00`: remain blocked by
full-discovery, source/snapshot, reviewed-corpus, reviewed-artifact, readiness,
rehearsal, and manual approval gates.

`OPS-HARDENING-00`, `PUBLIC-BETA-00`, `PUBLIC-1.0-00`: future gates.
