# AIDE Latest Task Packet

## PHASE

LOCAL-11 - LAN binding policy and safety gate

## GOAL

Prepare the next queue item after LOCAL-10 added the deterministic local
auto-test and auto-search harness.

## WHY

LOCAL-00 through LOCAL-10 established the Local Appliance track, explicit
instance bootstrap, migration guard, runtime composition, localhost service,
HTML workbench, hardened diagnostic pages, durable WorkUnit queue,
operator-gated local review/rebuild, deterministic local workers, and the
measurable auto-test/search harness.

LOCAL-11 is now recommended to define the LAN binding safety policy under an
explicit future task prompt.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-11/task.yaml`
- `runtime/local_eval/`
- `runtime/local_service/`
- `runtime/local_workbench/`
- `runtime/local_worker/`
- `control/inventory/local_10_next_task_decision.json`
- `control/audits/local-10-auto-test-search-harness-v0/`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-11 paths must come from a reviewed LOCAL-11 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-11/task.yaml`
- LOCAL-11 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-11 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-11 task branch from `dev`.
- Use the LOCAL-10 harness as safety evidence before enabling any LAN behavior.
- Keep LAN disabled until a future LOCAL-11 prompt explicitly scopes the policy and gates.
- Do not deploy.
- Do not run source probes, extraction, model/provider calls, or unsafe worker kinds unless a future prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-11 focused validator and tests when defined
- `python scripts/validate_local_auto_test_harness.py`
- `python scripts/validate_local_worker_runner.py`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No LAN binding without LOCAL-11 policy approval.
- No deployment.
- No source probe execution.
- No extraction execution.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-11 acceptance criteria must come from a future reviewed LOCAL-11 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`VALIDATION`, `RISKS`, and `NEXT`.
