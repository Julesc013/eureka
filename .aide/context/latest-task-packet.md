# AIDE Latest Task Packet

## PHASE

LOCAL-08 - Review and index rebuild from UI

## GOAL

Prepare the next queue item after LOCAL-07 added the durable local WorkUnit queue.

## WHY

LOCAL-00 through LOCAL-06 established the Local Appliance track, explicit instance bootstrap, migration guard, runtime composition, read-only localhost service, HTML workbench, and hardened diagnostic pages. LOCAL-07 adds the durable WorkUnit queue as a manifest-defined local store and CLI/demo/validator boundary, while keeping worker execution disabled.

LOCAL-08 is now recommended to add review and index rebuild UI under an explicit future task prompt.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-08/task.yaml`
- `runtime/workunit_queue/`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_WORKUNIT_QUEUE.md`
- `docs/reference/LOCAL_WORKUNIT_QUEUE_RUNTIME.md`
- `docs/reference/LOCAL_WORKUNIT_STATE_MACHINE.md`
- `docs/operations/LOCAL_WORKUNIT_QUEUE_RUNBOOK.md`
- `control/inventory/local_07_next_task_decision.json`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-08 paths must come from a reviewed LOCAL-08 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-08/task.yaml`
- LOCAL-08 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-08 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-08 task branch from `dev`.
- Use `runtime/local_appliance` and `runtime/workunit_queue` instead of ad hoc store paths.
- Keep LAN disabled.
- Do not deploy.
- Do not run source probes, workers, agents, extraction, or model/provider calls unless a future prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-08 focused validator and tests when defined
- `python scripts/validate_workunit_queue.py`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No LAN binding.
- No deployment.
- No source probe execution.
- No worker execution unless future scoped.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-08 acceptance criteria must come from a future reviewed LOCAL-08 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
