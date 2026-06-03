# Next Implementation Handoff

## Recommended Task

`INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT`

## Goal

Verify that indexless live search fallback can reuse the existing resolver,
source observation, review, gateway, and public projection paths without adding
a parallel UI/source path.

## Read First

- `docs/planning/public_live_preimplementation/IMPLEMENTATION_START_RECOMMENDATION.md`
- `docs/planning/public_live_preimplementation/architecture/INDEXLESS_LIVE_SEARCH_FALLBACK_SPEC.md`
- `docs/planning/public_live_preimplementation/authority/CURRENT_REPO_REALITY.md`
- `.aide/queue/index.yaml`
- `docs/architecture/RESOLUTION_RUN_KERNEL.md`
- `runtime/resolution_run/**`
- `runtime/engine/resolution_runs/**`
- `runtime/source/observation/**`
- `runtime/source/action/**`

## Exit Criteria

- authoritative implementation path chosen
- fallback acceptance checklist confirmed
- tests selected
- no runtime behavior change in preflight
- implementation task can proceed or blockers are explicit

