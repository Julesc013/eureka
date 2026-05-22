# AIDE Latest Task Packet

## PHASE

AIDE-BATCH-RUN-KERNEL-01

## GOAL

Add a portable headless Resolution Run Kernel before Workbench live-run wiring
or source-family expansion.

## WHY

The Workbench, CLI, API, TUI, native, relay, and snapshot clients should project
one reusable run kernel rather than directly calling IA-specific scripts.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/AIDE-BATCH-RUN-KERNEL-01/task.yaml`
- `.aide/queue/WORKBENCH-LIVE-RUN-01/task.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `contracts/resolution_run/`
- `runtime/resolution_run/`
- `scripts/eureka_resolution_run.py`
- `scripts/validate_resolution_run_kernel.py`
- `control/inventory/resolution_run_result.json`
- `docs/architecture/RESOLUTION_RUN_KERNEL.md`
- `control/audits/resolution-run-kernel-01-v0/`

## ALLOWED_PATHS

- `.aide/queue/AIDE-BATCH-RUN-KERNEL-01/**`
- `.aide/queue/WORKBENCH-LIVE-RUN-01/**`
- `.aide/queue/SOURCE-WAVE-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/resolution_run/**`
- `runtime/resolution_run/**`
- `scripts/eureka_resolution_run.py`
- `scripts/validate_resolution_run_kernel.py`
- `scripts/hunt_queue_progress.py`
- `scripts/validate_local_appliance_track.py`
- `tests/runtime/test_resolution_run_*.py`
- `tests/operations/test_resolution_run_scripts.py`
- `tests/operations/test_search_hunt_track.py`
- `tests/scripts/test_validate_resolution_run_kernel.py`
- `control/policies/resolution_run_*.json`
- `control/inventory/resolution_run_*.json`
- `examples/resolution_run/**`
- `docs/architecture/RESOLUTION_RUN_KERNEL.md`
- `docs/operations/RESOLUTION_RUN_KERNEL_RUNBOOK.md`
- `docs/operations/POST_RESOLUTION_RUN_KERNEL_PLAN.md`
- `docs/reference/RESOLUTION_RUN_PACKET.md`
- `docs/reference/RUN_EVENT_LOG.md`
- `docs/reference/RUN_COMMAND_BUS.md`
- `docs/reference/RUN_LANE_SNAPSHOT.md`
- `docs/reference/RUN_COVERAGE_REPORT.md`
- `control/audits/resolution-run-kernel-01-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `native/**`
- `crates/**`
- private local files
- committed operator tokens
- committed provider credentials
- raw prompts
- raw responses
- raw live IA response bodies

## NON_GOALS

- No Workbench live-run UI implementation.
- No live IA calls by default.
- No source probes, downloads, extraction, execution, model/provider calls, or deployment.
- No evidence, reviewed-record, source-cache, candidate, review, public, operator, or master-index mutation.
- No production readiness or public launch claim.

## IMPLEMENTATION

- Added resolution-run contracts, policies, matrices, docs, examples, and audit evidence.
- Added `runtime/resolution_run/` with in-memory run store, event log, policy gate, command handler, WorkUnit scheduler, lane projector, and dry-run kernel.
- Added CLI and validator over the same kernel.
- Added focused runtime, operation, and validator tests.

## ACCEPTANCE

- Dry-run run creation passes.
- Event log appends and reads events.
- Command bus applies safe commands and blocks unsafe commands.
- IA-Hunt WorkUnits are planned in dry-run only.
- Lane snapshots are emitted for operator, public, and native read-only projections.
- Boundary flags remain false.

## VALIDATION

- `python scripts/validate_resolution_run_kernel.py`
- `python -m unittest tests.runtime.test_resolution_run_kernel tests.runtime.test_resolution_run_projection tests.operations.test_resolution_run_scripts tests.scripts.test_validate_resolution_run_kernel`
- selected test lane router
- global validators as needed

## OUTPUT_SCHEMA

- Result: `control/inventory/resolution_run_result.json`
- Validation matrix: `control/inventory/resolution_run_validation_matrix.json`
- Next task decision: `control/inventory/resolution_run_next_task_decision.json`
- Audit report: `control/audits/resolution-run-kernel-01-v0/resolution_run_kernel_report.json`

## TOKEN_ESTIMATE

- Compact handoff-sized packet under AIDE Lite validation budget.

## COMMITS

- Planned: `feat(run): add resolution run kernel`

## EVIDENCE

- `control/inventory/resolution_run_validation_matrix.json`
- `control/inventory/resolution_run_result.json`
- `control/audits/resolution-run-kernel-01-v0/resolution_run_kernel_report.json`
- `control/audits/resolution-run-kernel-01-v0/generated/`
