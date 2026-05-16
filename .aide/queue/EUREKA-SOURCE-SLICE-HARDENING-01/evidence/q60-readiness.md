# Q60 Readiness

Readiness status: `READY_FOR_Q60_WITH_WARNINGS`

Recommended next task: `Q60 Eureka Object and Absence Surface v0`

## What Is Now Real

- Local fixture source observation.
- Deterministic normalized observation.
- Deterministic evidence candidate identity.
- Local review decision.
- Reviewed local index candidate.
- Positive search over the local reviewed index.
- Scoped absence report.
- Rejected review decision exclusion from local reviewed index.
- No-live/no-production-state boundary assertions.

## What Remains Fixture-Only

- Source data is synthetic/local fixture data.
- Review is deterministic local fixture review, not a product moderation/review workflow.
- Stores are temp or `.aide/queue/**` evidence-local, not production stores.
- Search/object/absence output is local reviewed-index behavior only.

## What Remains Missing

- Object/result/absence surface view model is still weak: Q58 returns public-index and absence records, not a dedicated object/absence surface contract.
- Duplicate limitation text appears in public-index-derived packets.
- No second source family or live source path should be added yet.

## Q60 Allowed Paths

Recommended exact allowed paths:

- `.aide/queue/EUREKA-OBJECT-ABSENCE-SURFACE-01/**`
- `.aide/reports/eureka-object-absence-surface.md`
- `.aide/reports/eureka-product-boundary-preservation.md`
- `.aide/reports/eureka-next-aide-task.md`
- `.aide/context/latest-task-packet.md`
- `runtime/local_foundry/fixture_source_observation_slice.py`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py`

Optional only if Q60 explicitly proves the need:

- a small new runtime-local view-model module under `runtime/local_foundry/**`;
- matching tests under the existing Q58 test files or a narrowly named `tests/runtime/test_fixture_object_absence_surface.py`.

## Q60 Forbidden Paths

- `.git/**`
- `.github/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `contracts/**` unless Q60 is split for reviewed contract work
- `surfaces/**`
- `site/**`
- `snapshots/**`
- `native/**`
- `crates/**`
- `examples/**`
- `evals/**`
- live connector/probe runtime files
- production source cache, evidence ledger, public index, or registry stores
- build/deploy/release outputs

## Warnings

- AIDE eval/golden failures remain outside Q59 scope.
- Git sync/dirty state remains for a coordinated multi-machine sync.
- Commit creation remains blocked by Git index write permissions.
