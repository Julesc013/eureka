# AIDE Latest Task Packet

## PHASE

`AIDE-BATCH-WORKBENCH-LIVE-RUN-01 — Project headless resolution runs into the local Workbench`

## GOAL

Project the headless `ResolutionRunKernel` into the local Workbench/API seam so a local query creates or displays a dry-run resolution run with `run_id`, state, events, lane snapshot, planned IA-HUNT dry-run WorkUnits, and blocked/deferred action posture.

## WHY

This makes Workbench the first browser/API projection over the shared run kernel instead of a separate search implementation. It keeps behavior in runtime, rendering in the local Workbench surface, and future source/live/review work behind policy gates.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/queue/WORKBENCH-LIVE-RUN-01/task.yaml`
- `runtime/resolution_run/`
- `runtime/local_service/`
- `runtime/local_workbench/`
- `scripts/eureka_resolution_run.py`
- `scripts/validate_resolution_run_kernel.py`

## ALLOWED_PATHS

- `contracts/resolution_run/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/resolution_run/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/local_eval/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/public_index/**`
- `runtime/candidate_index/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/review_queue/**`
- `surfaces/web/workbench/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `scripts/eureka_workbench_live_run.py`
- `scripts/validate_workbench_live_run.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_workbench_live_run*.py`
- `tests/operations/test_workbench_live_run*.py`
- `tests/scripts/test_validate_workbench_live_run.py`
- `examples/workbench/live_run/**`
- `control/policies/workbench_live_run*.json`
- `control/inventory/workbench_live_run*.json`
- `docs/architecture/WORKBENCH_LIVE_RUN.md`
- `docs/architecture/WORKBENCH_RUN_PROJECTION.md`
- `docs/operations/WORKBENCH_LIVE_RUN_RUNBOOK.md`
- `docs/operations/POST_WORKBENCH_LIVE_RUN_PLAN.md`
- `docs/reference/WORKBENCH_LIVE_RUN_ROUTES.md`
- `docs/reference/WORKBENCH_LIVE_RUN_API.md`
- `.aide/queue/**`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/workbench-live-run-01-v0/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `eureka-instance/**`
- `instances/**`
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Add Workbench live-run policies, route/API/projection/event/command matrices, examples, docs, audit pack, and result inventory.
- Add `runtime/local_service/workbench_live_run.py` as a projection wrapper over `runtime/resolution_run`.
- Add local service routes for the run list, run detail, and JSON resolution-run endpoints.
- Add local Workbench view models/renderers for run list/detail/search projection.
- Add CLI and validator scripts.
- Add focused runtime, operations, smoke, and validator tests.

## VALIDATION

- `python scripts/validate_workbench_live_run.py`
- `python scripts/eureka_workbench_live_run.py --query sampleproject --projection operator_workbench --dry-run --from-fixtures --include-ia-hunt-dry-run --json`
- `python scripts/eureka_workbench_live_run.py --query sampleproject --projection public_web --dry-run --from-fixtures --include-ia-hunt-dry-run --json`
- `python scripts/eureka_workbench_live_run.py --query sampleproject --projection native_desktop_read_only --dry-run --from-fixtures --include-ia-hunt-dry-run --json`
- `python -m unittest tests.runtime.test_workbench_live_run tests.runtime.test_workbench_live_run_projection tests.runtime.test_workbench_live_run_events tests.runtime.test_workbench_live_run_boundaries -v`
- `python -m unittest tests.operations.test_workbench_live_run_scripts tests.operations.test_workbench_live_run_smoke tests.scripts.test_validate_workbench_live_run -v`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`
- `python -m unittest discover -s tests -t .`

## COMMITS

- `feat(workbench): project resolution runs locally`

## EVIDENCE

- Workbench live-run validator: PASS.
- Operator, public, and native read-only CLI projections: PASS.
- Focused Workbench live-run tests: PASS.
- Test selector and selected focused lanes: PASS.
- Cross-stack validators through resolution run, G0, F0, SCOUT, DOMAIN, SYN, IA-HUNT, Workbench result lanes, search interaction, foundation, test lane policy, contract taxonomy, and repo structure canon: PASS with existing repo-structure warnings.
- Final AIDE checks, generated artifact cleanliness after commit, commit check, and full discovery remain closeout items until run.

## NON_GOALS

- No live IA metadata calls.
- No source probes or public source fanout.
- No downloads/uploads, extraction, execution, install, emulation, model/provider calls, or deployment.
- No operator instance mutation, master index mutation, source-cache/evidence/candidate/reviewed-index mutation.
- No browser review/promote flow, Local Apply Gate, WebSocket/SSE, SOURCE-WAVE, or IA live metadata lane implementation.
- No production readiness or public launch claim.

## ACCEPTANCE

- Workbench uses the Resolution Run Kernel and emits run packet, events, lanes, WorkUnits, and blocked actions.
- Operator, public, and native read-only projections pass.
- Blocked commands return policy-blocked responses without mutation.
- Focused validators/tests and full discovery pass, or exact deferral is recorded.
- Commit is pushed to `dev`; `main` is not pushed.

## OUTPUT_SCHEMA

Return the requested closeout report with `STATUS`, `SUMMARY`, `COMMITS`, `WORKBENCH_LIVE_RUN`, `VALIDATION`, `PUSH`, `BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- Packet target: compact, under AIDE validation limits.
- Full prompt/history intentionally excluded.
