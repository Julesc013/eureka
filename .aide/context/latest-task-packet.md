# AIDE Latest Task Packet

## PHASE

LOCAL-05 - HTML workbench v0

## GOAL

Add the first minimal HTML workbench over the LOCAL-04 read-only localhost HTTP service.

## WHY

LOCAL-01 established explicit instance bootstrap. LOCAL-02 added instance configuration, schema, and migration guard. LOCAL-03 added the local runtime composition boundary. LOCAL-04 added the read-only localhost HTTP service over the reviewed public index.

LOCAL-05 should build the first workbench surface on that service boundary without enabling LAN, writes, source probes, WorkUnits, index rebuilds, deployment, production readiness, or public launch readiness.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-05/task.yaml`
- `runtime/local_service/`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_HTTP_SERVICE.md`
- `docs/reference/LOCAL_HTTP_API.md`
- `docs/operations/LOCAL_HTTP_SERVICE_RUNBOOK.md`
- `control/inventory/local_04_next_task_decision.json`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-05 paths must come from the reviewed LOCAL-05 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-05/task.yaml`
- LOCAL-05 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless the reviewed LOCAL-05 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-05 task branch from `dev`.
- Use the LOCAL-04 HTTP service boundary for workbench reads.
- Keep the workbench read-only unless a future task explicitly enables writes.
- Do not expose LAN.
- Do not deploy.
- Do not run source probes or WorkUnits.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-05 focused validator and tests when defined
- `python scripts/validate_local_http_service.py`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No LAN binding.
- No deployment.
- No source probe execution.
- No WorkUnit execution.
- No review mutation.
- No index rebuild behavior.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-05 acceptance criteria are met after a future reviewed LOCAL-05 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
