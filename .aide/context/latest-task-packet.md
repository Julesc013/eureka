# AIDE Latest Task Packet

## PHASE

LOCAL-01 - Local instance layout and bootstrap

## GOAL

LOCAL-01 - Define explicit local instance root layout and bootstrap posture for the Local Appliance.

## WHY

LOCAL-00 inserted the Local Appliance / Local Network Workbench track before F0 so future product work proves behavior through a real local hosted system. F0 remains resumable but is deferred until LOCAL-14 closes the Local Appliance track.

## CONTEXT_REFS

- `control/inventory/local_appliance_next_task_decision.json`
- `control/inventory/local_appliance_track_plan.json`
- `control/inventory/local_appliance_readiness_matrix.json`
- `control/inventory/f0_deferral_for_local_appliance.json`
- `control/policies/local_appliance_policy.json`
- `control/policies/local_network_safety_policy.json`
- `control/policies/local_agent_workunit_policy.json`
- `control/policies/future_task_behavior_gate_policy.json`
- `control/policies/local_track_completion_policy.json`
- `docs/operations/LOCAL_APPLIANCE_TRACK.md`
- `docs/operations/LOCAL_TRACK_COMPLETION_STANDARD.md`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-01/task.yaml`
- control, docs, scripts, and tests paths explicitly named by the reviewed LOCAL-01 prompt

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
- raw provider credentials, API keys, local caches, raw prompt logs

## IMPLEMENTATION

- Start from `main` or a task branch from `main`.
- Read the LOCAL-00 policy and inventory refs first.
- Keep LOCAL-01 focused on explicit instance layout and bootstrap posture.
- Do not implement the HTTP server.
- Do not implement the HTML workbench.
- Do not expose LAN.
- Do not deploy.
- Do not claim production readiness or public launch readiness.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_local_appliance_track.py`
- `python -m unittest tests.operations.test_local_appliance_track`
- additional LOCAL-01 validators/tests defined by the reviewed LOCAL-01 task
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`

## COMMITS

- Commit coherent subdeliverables with structured bodies.
- Do not mutate `main` or `dev` except by an explicit reviewed branch workflow.

## EVIDENCE

- changed files
- validation commands and results
- verifier result
- review packet path and result when review-pack is available
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

- LOCAL-01 acceptance criteria are met.
- Local Appliance policies remain in force.
- No forbidden product/runtime paths are modified unless LOCAL-01 explicitly authorizes them.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
- warnings:
  - none
