# File Change Plan

Expected implementation file changes for `INDEXLESS-LIVE-SEARCH-FALLBACK-00`.

| Classification | Path | Reason | Risk | Related tests | Rollback note |
| --- | --- | --- | --- | --- | --- |
| expected modify | `runtime/engine/resolution_runs/service.py` | Add fallback policy gate and provider invocation after local miss. | Could change existing search run behavior. | `runtime/engine/resolution_runs/tests/test_service.py` | Remove fallback branch/constructor options. |
| expected modify | `runtime/engine/interfaces/public/resolution_run.py` | Add backwards-compatible fallback lane/result fields if notices are insufficient. | Public envelope compatibility. | `runtime/gateway/tests/test_resolution_runs_view_models.py` | Keep fields optional or remove extension. |
| expected modify | `runtime/engine/resolution_runs/resolution_run.py` | Serialize/deserialize new optional run fields if added. | Run store compatibility. | `runtime/engine/resolution_runs/tests/test_run_store.py` | Remove optional fields; existing records still load. |
| expected modify | `runtime/engine/resolution_runs/run_store.py` | Possibly tolerate/load fallback fields. | Persistence drift. | `runtime/engine/resolution_runs/tests/test_run_store.py` | Revert serialization changes. |
| maybe modify | `runtime/source/observation/archive_org_public_metadata.py` | Expose provider result shape or policy controls for engine fallback. | Could affect existing public-search provider tests. | `tests/runtime/test_archive_org_public_metadata_candidates.py` | Keep adapter-compatible wrapper instead. |
| maybe modify | `runtime/source/action/action_kernel.py` | Reuse source action request/observation plan if provider moves through source-action seam. | Broad source-action tests. | `tests/runtime/test_source_action_kernel.py` | Avoid unless needed. |
| maybe modify | `runtime/candidate_store/runtime.py` | Normalize fallback source candidates into existing candidate records. | Candidate state naming drift. | `tests/runtime/test_candidate_store_runtime.py` | Use local mapper in engine service instead. |
| maybe modify | `runtime/search/need/**` | Create or project SearchNeed for no-candidate fallback misses. | Public/private need boundary. | `tests/runtime/test_search_need_*` | Return run-local need state first. |
| maybe modify | `runtime/gateway/public_api/resolution_runs_boundary.py` | Project optional fallback run fields. | API compatibility. | `runtime/gateway/tests/test_resolution_runs_boundary.py` | Keep optional fields absent when empty. |
| maybe modify | `runtime/gateway/public_api/resolution_runs_view_models.py` | Validate/project optional fallback fields. | View-model strictness. | `runtime/gateway/tests/test_resolution_runs_view_models.py` | Keep extensions optional. |
| maybe modify | `runtime/gateway/public_api/public_search.py` | De-risk existing source-policy hook or project engine fallback result. | Direct source shortcut risk. | `runtime/gateway/tests/test_public_search_api.py` | Keep existing local-index-only behavior. |
| maybe modify | `surfaces/web/workbench/**` | Only if operator must inspect fallback run output in the same task. | Surface scope creep. | `tests/runtime/test_workbench_review_*` | Defer to `WORKBENCH-RUN-REVIEW-PROJECTION-00`. |
| expected add | `runtime/engine/resolution_runs/tests/test_fallback.py` or extend `test_service.py` | Focused engine fallback behavior. | None if narrow. | new test file | Remove with implementation rollback. |
| expected add | `runtime/gateway/tests/test_public_search_fallback_boundary.py` or extend existing API tests | Public direct-source and operator action leakage tests. | None if narrow. | new or existing tests | Remove with implementation rollback. |
| avoid | `contracts/**` | Live contract edits are not required unless implementation cannot map statuses. | Contract churn. | contract tests | Run semantic-core task first if needed. |
| avoid | `docs/canon/**` | Canon authority not part of fallback implementation. | Authority churn. | none | Do not touch. |
| protected | `.aide/queue/current.toml` | Queue state must not mutate. | Task-state corruption. | none | Do not touch. |
| protected | new top-level roots | Closed-root architecture rule. | Architecture drift. | architecture checks | Do not create. |
