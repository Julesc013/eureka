# AIDE Latest Task Packet

## PHASE

LOCAL-09 - Deterministic local worker runner

## GOAL

Prepare the next queue item after LOCAL-08 added the operator-gated local review/rebuild loop.

## WHY

LOCAL-00 through LOCAL-08 established the Local Appliance track, explicit
instance bootstrap, migration guard, runtime composition, localhost service,
HTML workbench, hardened diagnostic pages, durable WorkUnit queue, and
operator-gated local review/rebuild loop.

LOCAL-09 is now recommended to add a deterministic local worker runner under an
explicit future task prompt.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-09/task.yaml`
- `runtime/workunit_queue/`
- `runtime/local_review/`
- `runtime/local_operator/`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_REVIEW_REBUILD_LOOP.md`
- `docs/reference/LOCAL_REVIEW_API.md`
- `docs/reference/LOCAL_OPERATOR_AUTH.md`
- `control/inventory/local_08_next_task_decision.json`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-09 paths must come from a reviewed LOCAL-09 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-09/task.yaml`
- LOCAL-09 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-09 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-09 task branch from `dev`.
- Use `runtime/local_appliance`, `runtime/workunit_queue`, and `runtime/local_review` instead of ad hoc store paths.
- Keep LAN disabled.
- Do not deploy.
- Do not run source probes, workers, extraction, or model/provider calls unless a future prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-09 focused validator and tests when defined
- `python scripts/validate_local_review_rebuild.py`
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

- LOCAL-09 acceptance criteria must come from a future reviewed LOCAL-09 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
