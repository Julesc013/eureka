# Q61 Readiness

## Status

`READY_FOR_Q61_WITH_WARNINGS`

## Recommended Q61

`Q61 Eureka Reviewed Index Persistence v0`

## Why

Q60 makes the first fixture loop inspectable through stable result, object/detail, evidence summary, source/provenance, and absence packets. The next weakest product step is persistence discipline for reviewed local index candidates: storing and reloading the reviewed fixture index in a deliberate local-only path without confusing it with production public index state.

## Now Real

- Deterministic fixture source observation.
- Deterministic normalized observation.
- Evidence candidate and accepted local review decision.
- Reviewed local index candidate.
- Positive search result and bounded absence report.
- Deterministic result/object/evidence/source/absence packets.
- Tests for representation refs, determinism, no-live flags, and malformed packet validation.

## Still Fixture-Only

- Source family.
- Evidence/review/index data.
- Search/object/absence scope.
- Surface packets.

## Missing / Deferred

- Durable reviewed-index persistence policy and reload tests outside transient evidence stores.
- Second source fixture.
- Local API/static renderer.
- Production public index publication.
- Live source permissioning.

## Q61 Allowed Paths

- `.aide/queue/EUREKA-REVIEWED-INDEX-PERSISTENCE-01/**`
- `.aide/reports/eureka-reviewed-index-persistence.md`
- `.aide/reports/eureka-product-boundary-preservation.md`
- `.aide/reports/eureka-next-aide-task.md`
- `.aide/context/latest-task-packet.md`
- `runtime/local_foundry/fixture_source_observation_slice.py`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py`
- Optional new tests under `tests/runtime/**` only if they target the existing local fixture persistence behavior.

## Q61 Forbidden Paths / Operations

Do not use live probes, network, providers/models, source sync, registry mutation, production source-cache writes, production evidence-ledger writes, production public-index writes, site deploy, release publish, branch mutation, or a second source family.

## Warnings

- AIDE golden eval still has 9 failures unrelated to Q60 product behavior.
- Current local `dev` remains dirty and diverged from origin/dev due multi-machine local work.
- Q60 was not committed in isolation because its product/test files remain untracked together with prior Q58/Q59 slice files and are not safely separable in the current worktree.
