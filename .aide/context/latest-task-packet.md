# AIDE Latest Task Packet

## PHASE

LOCAL-03 - Local runtime composition boundary

## GOAL

LOCAL-03 - Define the local service, store, worker, and workbench composition boundary after versioned instance configuration.

## WHY

LOCAL-02 adds explicit instance schema versioning, store manifests, migration state, and a read-only migration status guard. LOCAL-03 should define how local service, store, worker, and future workbench layers compose without collapsing boundaries or starting the HTTP server yet.

Compatibility note: LOCAL-03 is the current main development lane inside the LOCAL-MVP-FOUNDATION appliance route before F0. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## CONTEXT_REFS

- `control/inventory/local_instance_schema_version.json`
- `control/inventory/local_instance_config_schema.json`
- `control/inventory/local_instance_store_manifest_schema.json`
- `control/inventory/local_instance_migration_state_schema.json`
- `control/inventory/local_instance_migration_guard_result.json`
- `control/inventory/local_02_leakage_baseline.json`
- `control/inventory/local_02_next_task_decision.json`
- `control/policies/local_instance_schema_policy.json`
- `control/policies/local_instance_migration_policy.json`
- `docs/reference/LOCAL_INSTANCE_CONFIG_SCHEMA.md`
- `docs/reference/LOCAL_INSTANCE_MIGRATION_GUARD.md`
- `docs/operations/LOCAL_INSTANCE_MIGRATION_POLICY.md`
- `.aide/queue/LOCAL-02/task.yaml`
- `.aide/queue/LOCAL-03/task.yaml`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-03/task.yaml`
- future LOCAL-03 control, docs, scripts, and tests paths explicitly named by a reviewed LOCAL-03 prompt

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `runtime/**` unless a future LOCAL task explicitly authorizes implementation
- `contracts/**` unless a future LOCAL task explicitly authorizes contract edits
- `surfaces/**`
- `site/**`
- `site/dist/**`
- `native/**`
- `crates/**`
- `examples/**`
- `eureka-instance/**`
- raw provider credentials, API keys, local caches, raw prompt logs

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-03 task branch from `dev`.
- Keep F0 deferred until LOCAL-14.
- Use the LOCAL-02 versioned instance boundary.
- Do not implement the HTTP server.
- Do not implement the HTML workbench.
- Do not expose LAN.
- Do not deploy.
- Do not claim production readiness or public launch readiness.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_local_instance_migration_guard.py`
- additional LOCAL-03 validators/tests defined by the reviewed LOCAL-03 task
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/check_architecture_boundaries.py`
- AIDE doctor/validate/test/selftest/verify/review-pack when practical

## COMMITS

- Commit coherent subdeliverables with structured bodies.
- Merge completed task branches back to `dev` for shared live-agent access when the task passes or passes with warning-only pre-existing debt.

## EVIDENCE

- LOCAL-02 audit pack: `control/audits/local-02-instance-configuration-migration-guard-v0/`
- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No F0 implementation.
- No extraction runtime implementation.
- No HTTP server implementation.
- No HTML workbench implementation.
- No WorkUnit runtime implementation.
- No LAN binding.
- No live source calls.
- No model/provider calls.
- No deployment.

## ACCEPTANCE

- LOCAL-03 acceptance criteria are met.
- Local Appliance policies remain in force.
- No forbidden product/runtime paths are modified unless LOCAL-03 explicitly authorizes them.
- No local instance state is committed.
- No production readiness or public launch readiness is claimed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
- warnings:
  - none
