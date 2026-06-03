# INDEXLESS-LIVE-SEARCH-FALLBACK-00 Implementation Task Plan

## Task ID

`INDEXLESS-LIVE-SEARCH-FALLBACK-00`

## Goal

Implement the smallest useful indexless live search fallback slice as a
governed engine resolution-run mode.

## Required Reading

- `AGENTS.md`
- `.aide/context/latest-task-packet.md`
- this preflight directory
- `docs/planning/public_live_preimplementation/architecture/INDEXLESS_LIVE_SEARCH_FALLBACK_SPEC.md`
- `docs/planning/public_live_preimplementation/public_scope/PUBLIC_ACTION_POLICY_DRAFT.md`
- likely implementation files listed in `FILE_CHANGE_PLAN.md`

## Selected Resolver Path Decision

```text
DECISION: USE_EXISTING_ENGINE_RESOLUTION_RUNS_PATH
```

## Allowed Files

Implementation may modify focused files under existing roots only, especially:

- `runtime/engine/resolution_runs/**`
- `runtime/engine/interfaces/public/**`
- `runtime/source/action/**`
- `runtime/source/observation/**`
- `runtime/candidate_store/**`
- `runtime/search/need/**`
- `runtime/gateway/public_api/**`
- focused tests under `runtime/**/tests` and `tests/**`

Do not create new top-level roots.

## Protected Files

Do not mutate queue state or protected paths unless the implementation prompt
explicitly permits them. In particular, do not mutate canon docs, archives, or
unrelated runtime/surface modules.

## Step-By-Step Sequence

1. Re-run task guard for `INDEXLESS-LIVE-SEARCH-FALLBACK-00`.
2. Confirm current working tree state and current branch.
3. Add a fallback policy/config object or constructor options to
   `LocalResolutionRunService`.
4. Keep current local reviewed/result path unchanged.
5. In `_run_search`, after no local results or supported insufficient result,
   evaluate fallback enabled/source allowlist/budget/projection policy.
6. If fallback is disabled, attach honest degraded state/notice and do not call
   a provider.
7. If source family is disabled, attach policy-blocked/unavailable state and do
   not call a provider.
8. If allowed, invoke the allowlisted metadata-only source adapter/provider
   behind the engine run service.
9. Convert source output to SourceObservation/equivalent and candidate or need
   state.
10. Persist fallback candidate/need/degraded lane in the run record or a
    backwards-compatible extension.
11. Project public-safe fallback results only through gateway/view-model code.
12. Add focused tests for all hard constraints.
13. Run focused validation.
14. Stage and commit coherent implementation if validation passes.

## Expected Changed Files

See `FILE_CHANGE_PLAN.md`.

## Expected New Tests

- Engine run service fallback policy and provider tests.
- Public projection/action leakage tests.
- Source failure/budget disabled tests.
- Truth-boundary tests.

## Policy Gates To Preserve

- fallback is a run mode
- fallback is source-allowlisted
- fallback is budgeted
- fallback is policy-gated
- fallback can be disabled
- source family can be disabled
- fallback never promotes truth
- fallback output is candidate/need/policy_blocked/unavailable, not verified
- public UI does not call sources directly
- public UI does not expose operator-only actions
- review remains the truth boundary

## Degradation States

Use or map to:

- `candidate`
- `need`
- `near_miss` only where existing support already exists
- `policy_blocked`
- `unknown` or `unavailable`

Do not add new status names if current vocabulary can map them.

## Validation Commands

Minimum:

```text
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
```

Focused tests:

```text
py -3 -m unittest runtime.engine.resolution_runs.tests.test_service
py -3 -m unittest runtime.gateway.tests.test_public_search_api
```

Add source/candidate tests according to actual changed files.

## Commit Expectation

If implementation and validation pass, stage only coherent changed files and
commit them. Suggested subject:

```text
feat(search): add governed indexless live fallback
```

## Exit Criteria

- fallback attaches to engine resolution-runs path
- local result path unchanged
- local miss can produce governed candidate/need/degraded state
- fallback/source disabled states are honest
- no public direct source shortcut
- no reviewed truth promotion
- focused validation passes or warnings are documented
