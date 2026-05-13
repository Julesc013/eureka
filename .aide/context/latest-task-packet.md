# AIDE Latest Task Packet

## PHASE

LOCAL-07 - Operator-gated WorkUnit queue

## GOAL

Add the first operator-gated WorkUnit queue after LOCAL-06 hardened the read-only local workbench pages.

## WHY

LOCAL-01 established explicit instance bootstrap. LOCAL-02 added instance configuration, schema, and migration guard. LOCAL-03 added the local runtime composition boundary. LOCAL-04 added the read-only localhost HTTP service over the reviewed public index. LOCAL-05 added the minimal server-rendered HTML workbench.

LOCAL-06 hardened status, search, object, source, absence, and home pages with store status, provenance, local-only scope, current-index absence semantics, non-claims, and unavailable capability markers. LOCAL-07 is now recommended so WorkUnit queue work can start from that read-only operational surface.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-07/task.yaml`
- `runtime/local_workbench/`
- `runtime/local_service/`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_HTML_WORKBENCH.md`
- `docs/reference/LOCAL_HTML_ROUTES.md`
- `docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md`
- `control/inventory/local_06_next_task_decision.json`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-07 paths must come from a reviewed LOCAL-07 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-07/task.yaml`
- LOCAL-07 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-07 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-07 task branch from `dev`.
- Use the LOCAL-04 HTTP service boundary for workbench reads.
- Keep the workbench read-only unless a future task explicitly enables writes.
- Do not expose LAN.
- Do not deploy.
- Do not run source probes or agents.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-07 focused validator and tests when defined
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

- LOCAL-07 acceptance criteria are met after a future reviewed LOCAL-07 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
