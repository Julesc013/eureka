# AIDE Latest Task Packet

## PHASE

LOCAL-02 - Instance configuration, schema, and migration guard

## GOAL

LOCAL-02 - Define local instance configuration schema and safe migration guard after the explicit LOCAL-01 instance bootstrap.

## WHY

LOCAL-01 adds explicit local instance roots and bootstrap/validation/status commands. LOCAL-02 should make the instance configuration contract governed and add migration refusal/rollback posture before any service or workbench implementation starts.

## CONTEXT_REFS

- `control/inventory/local_instance_layout.json`
- `control/inventory/local_instance_bootstrap_result.json`
- `control/inventory/local_instance_validation_result.json`
- `control/inventory/local_instance_gap_register.json`
- `control/inventory/local_01_leakage_baseline.json`
- `control/inventory/local_01_next_task_decision.json`
- `control/policies/local_instance_policy.json`
- `control/policies/local_instance_path_policy.json`
- `control/policies/local_instance_state_policy.json`
- `docs/architecture/LOCAL_INSTANCE_MODEL.md`
- `docs/reference/LOCAL_INSTANCE_LAYOUT.md`
- `docs/operations/LOCAL_INSTANCE_BOOTSTRAP.md`
- `.aide/queue/LOCAL-02/task.yaml`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-02/task.yaml`
- future LOCAL-02 control, docs, scripts, and tests paths explicitly named by a reviewed LOCAL-02 prompt

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

- Start from `dev` or an explicit LOCAL-02 task branch from `dev`.
- Keep F0 deferred until LOCAL-14.
- Build on LOCAL-01 bootstrap commands without starting a server or workbench.
- Do not implement the HTTP server.
- Do not implement the HTML workbench.
- Do not expose LAN.
- Do not deploy.
- Do not claim production readiness or public launch readiness.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_local_instance_bootstrap.py`
- additional LOCAL-02 validators/tests defined by the reviewed LOCAL-02 task
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/check_architecture_boundaries.py`
- AIDE doctor/validate/test/selftest/verify/review-pack when practical

## COMMITS

- Commit coherent subdeliverables with structured bodies.
- Merge completed task branches back to `dev` for shared live-agent access when the task passes or passes with warning-only pre-existing debt.

## EVIDENCE

- LOCAL-01 audit pack: `control/audits/local-01-local-instance-bootstrap-v0/`
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

- LOCAL-02 acceptance criteria are met.
- Local Appliance policies remain in force.
- No forbidden product/runtime paths are modified unless LOCAL-02 explicitly authorizes them.
- No local instance state is committed.
- No production readiness or public launch readiness is claimed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
- warnings:
  - none
