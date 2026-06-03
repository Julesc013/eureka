DECISION: USE_EXISTING_ENGINE_RESOLUTION_RUNS_PATH

# Resolver Path Decision

## Rationale

The existing engine resolution-runs service is the safest current attachment
point for indexless fallback because it already owns the persistent run
boundary:

- run identity and persistence
- local exact/search execution
- checked source summaries
- bounded absence reports
- gateway-facing service interface

This keeps fallback behind a run service instead of letting public search or UI
routes call source providers directly.

## Evidence From Repo Paths

- `runtime/engine/resolution_runs/service.py` allocates runs, executes
  deterministic search, records checked sources, records absence reports, and
  persists through `LocalResolutionRunStore`.
- `runtime/engine/interfaces/service/resolution_run_service.py` is the service
  protocol used by gateway public APIs.
- `runtime/gateway/public_api/resolution_runs_boundary.py` projects runs from
  the service and does not own source behavior.
- `runtime/resolution_run/run_kernel.py` proves useful event/workunit/policy
  concepts, but it is in-memory dry-run behavior and blocks live source actions.
- `runtime/gateway/public_api/public_search.py` has an optional Archive.org
  candidate provider hook; using that hook as the primary fallback path would
  put fallback too close to the forbidden UI/search route -> source call path.

## Confidence

High.

The engine path is current, tested, persistent, and aligned with repo dependency
law. The gaps are additive and testable.

## Risks

- `ResolutionRunRecord` lacks explicit fallback, WorkUnit, SourceObservation,
  RunEvent, and candidate/need lane fields.
- Existing public search candidate-provider behavior is already a surface-level
  hook; next implementation must not expand it as the authoritative fallback.
- Existing policy controls are distributed across run, source action, IA probe,
  public API, and candidate-store modules.
- Status names currently vary across runtime modules.

## Rejected Alternatives

### USE_EXISTING_RESOLUTION_RUN_PATH

Rejected as the primary attach point because `runtime/resolution_run/**` is
dry-run/in-memory and intentionally blocks live/source execution. It should
inform event and policy naming, not own the first persistent fallback slice.

### CREATE_THIN_ADAPTER_OVER_EXISTING_SEARCH_PATH

Rejected as the primary attach point because plain search services and public
search routes do not own run truth. A search wrapper could be useful inside the
engine run service, but making it the main path risks a parallel source/search
lane.

### BLOCK_IMPLEMENTATION_PENDING_REPO_CLARIFICATION

Rejected because the repo has a clear current engine run seam and enough source,
candidate, need, and public-safety infrastructure to implement a small governed
fallback slice.

## Likely Files For Next Implementation Task

Expected or likely:

- `runtime/engine/resolution_runs/service.py`
- `runtime/engine/interfaces/public/resolution_run.py`
- `runtime/engine/resolution_runs/resolution_run.py`
- `runtime/engine/resolution_runs/run_store.py`
- `runtime/engine/resolution_runs/tests/test_service.py`
- `runtime/source/observation/archive_org_public_metadata.py`
- `runtime/source/action/action_kernel.py`
- `runtime/candidate_store/runtime.py`
- `runtime/search/need/**`
- `runtime/gateway/public_api/resolution_runs_boundary.py`
- `runtime/gateway/public_api/resolution_runs_view_models.py`
- `runtime/gateway/public_api/public_search.py` only for projection or to
  de-risk existing source-policy behavior

## Required Tests

- Local reviewed/result run path unchanged.
- Index unavailable or local insufficient run produces fallback candidate or
  need, never verified truth.
- Fallback disabled returns honest unavailable/need/policy-blocked state.
- Source disabled returns policy-blocked or unavailable state.
- Timeout and budget exceeded degrade without truth promotion.
- Public route does not directly call source providers.
- Public route does not expose operator-only actions.
- Run record persists fallback notices/lane state.

## Rollback Plan

The fallback implementation should be small enough to roll back by:

1. Removing injected fallback policy/provider from the engine resolution-runs
   service.
2. Reverting new fallback fields or keeping them empty/backward compatible.
3. Leaving existing local search and absence reports unchanged.
4. Keeping public search in `local_index_only` mode.

## Protected Paths Avoided In This Preflight

This preflight did not modify live runtime, contracts, surfaces, site,
snapshots, native, crates, release, schema, canon, or queue paths.
