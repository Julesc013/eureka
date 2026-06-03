# Execution Queue

This queue preserves the mega-prompt dependency order but reconciles it with
current repo authority.

## Immediate Queue

1. `INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT`
2. `INDEXLESS-LIVE-SEARCH-FALLBACK-00`
3. `SEARCH-USEFULNESS-EVAL-00`
4. `REVIEWED-ARTIFACT-RECORD-GATE-00`
5. `PUBLIC-ALPHA-READINESS-RECHECK-00`

## Reconciled Mega Queue

`AUTHORITY-LOCK-00`: satisfied for this package; rerun before product edits.

`PUBLIC-SCOPE-V1-00`: partially satisfied by current docs; keep read-only,
bounded, no public fanout, no public mutation.

`SEMANTIC-CORE-CONTRACTS-00`: mostly satisfied by TSIS-00; run only as a gap
audit unless existing contracts fail fallback needs.

`RESOLVER-SPINE-00`: partially satisfied by existing runtime paths; use as an
alignment task, not a greenfield rewrite.

`INDEXLESS-LIVE-SEARCH-FALLBACK-00`: current recommended implementation task.

`REVIEW-LEDGER-00`: audit and reinforce review/promotion invariants.

`WORKBENCH-RUN-REVIEW-PROJECTION-00`: extend only if fallback evidence cannot
be inspected through existing Workbench projections.

`SURFACE-KERNEL-00` and `BASELINE-RENDERERS-00`: continue after fallback output
requires cross-render parity beyond current public/snapshot renderers.

`HARD-QUERY-EVAL-00` and `REVIEWED-SEED-CORPUS-00`: required before any renewed
public launch approval.

`PUBLIC-ALPHA-READINESS-00` and `PUBLIC-ALPHA-LAUNCH-00`: remain blocked by
manual approval and usefulness/corpus gates.

`OPS-HARDENING-00`, `PUBLIC-BETA-00`, `PUBLIC-1.0-00`: future gates.

