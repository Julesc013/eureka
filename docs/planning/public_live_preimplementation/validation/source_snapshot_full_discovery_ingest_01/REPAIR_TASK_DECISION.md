# Repair Task Decision

## Decision

```text
DECISION: RUN ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01
```

## Rationale

The external summary is terminal, current to `HEAD`, and red. The prompt
priority places architecture-boundary drift ahead of generated-artifact,
source/snapshot, queue, legacy-leakage, and test-fixture drift.

Architecture-related evidence includes:

- R0 legacy runtime leakage validation reports
  `runtime/source/observation/internet_archive_live_transport.py`.
- Runtime architecture leakage validation reports production-looking task/control
  vocabulary in `contracts/publication/public_alpha_ux_mvp_reassess.v0.json`.
- Repo-structure strict validation exits non-zero.
- Repo-structure canon validation reports unresolved `scripts` debt.

## Rejected Alternatives

`QUEUE-HANDOFF-DRIFT-REPAIR-01` is not rejected permanently. It is the largest
failure family by count and should follow after architecture/leakage blockers
are resolved or reclassified.

`SOURCE-SNAPSHOT-FAILURE-REPAIR-01` is too broad for the first repair pass.

`PUBLIC-ALPHA-READINESS-00` is blocked by full discovery, reviewed corpus, and
reviewed artifact gates.

`DEV-TO-MAIN-PROMOTION-REVIEW-*` is blocked by red full discovery and current
branch divergence.

## Rollback

This ingest task writes only report files. Rollback is deleting this validation
package if the external summary is later superseded by a rerun.
