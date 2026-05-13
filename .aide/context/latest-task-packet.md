# AIDE Latest Task Packet

## PHASE

LOCAL-06 - Status, object, source, and absence page hardening

## GOAL

Harden the first LOCAL-05 HTML workbench pages while preserving the LOCAL-04 read-only localhost service and LOCAL-03 runtime composition boundary.

## WHY

LOCAL-01 established explicit instance bootstrap. LOCAL-02 added instance configuration, schema, and migration guard. LOCAL-03 added the local runtime composition boundary. LOCAL-04 added the read-only localhost HTTP service over the reviewed public index. LOCAL-05 added the minimal server-rendered HTML workbench.

LOCAL-06 should improve the status, object, source, and absence page behavior without enabling LAN, writes, source probes, WorkUnits, index rebuilds, deployment, production readiness, or public launch readiness.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-06/task.yaml`
- `runtime/local_workbench/`
- `runtime/local_service/`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_HTML_WORKBENCH.md`
- `docs/reference/LOCAL_HTML_ROUTES.md`
- `docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md`
- `control/inventory/local_05_next_task_decision.json`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-06 paths must come from a reviewed LOCAL-06 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-06/task.yaml`
- LOCAL-06 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-06 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-06 task branch from `dev`.
- Use the LOCAL-04 HTTP service boundary for workbench reads.
- Keep the workbench read-only unless a future task explicitly enables writes.
- Do not expose LAN.
- Do not deploy.
- Do not run source probes or WorkUnits.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-06 focused validator and tests when defined
- `python scripts/validate_local_html_workbench.py`
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

- LOCAL-06 acceptance criteria are met after a future reviewed LOCAL-06 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
