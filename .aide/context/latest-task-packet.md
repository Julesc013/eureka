# AIDE Latest Task Packet

## PHASE

LOCAL-10 - Auto-test and auto-search harness

## GOAL

Prepare the next queue item after LOCAL-09 added the deterministic local worker runner.

## WHY

LOCAL-00 through LOCAL-09 established the Local Appliance track, explicit
instance bootstrap, migration guard, runtime composition, localhost service,
HTML workbench, hardened diagnostic pages, durable WorkUnit queue, and
operator-gated local review/rebuild loop, then added deterministic local
worker execution over WorkUnits.

LOCAL-10 is now recommended to add the auto-test and auto-search harness under an
explicit future task prompt.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-10/task.yaml`
- `runtime/local_worker/`
- `runtime/workunit_queue/`
- `runtime/local_review/`
- `runtime/local_operator/`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_REVIEW_REBUILD_LOOP.md`
- `docs/reference/LOCAL_REVIEW_API.md`
- `docs/reference/LOCAL_OPERATOR_AUTH.md`
- `control/inventory/local_09_next_task_decision.json`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-10 paths must come from a reviewed LOCAL-10 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-10/task.yaml`
- LOCAL-10 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-10 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-10 task branch from `dev`.
- Use `runtime/local_appliance`, `runtime/workunit_queue`, and `runtime/local_review` instead of ad hoc store paths.
- Keep LAN disabled.
- Do not deploy.
- Do not run source probes, extraction, model/provider calls, or unsafe worker kinds unless a future prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-10 focused validator and tests when defined
- `python scripts/validate_local_worker_runner.py`
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
- No worker expansion beyond LOCAL-09 enabled deterministic kinds unless future scoped.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-10 acceptance criteria must come from a future reviewed LOCAL-10 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
