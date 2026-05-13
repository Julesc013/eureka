# AIDE Latest Task Packet

## PHASE

LOCAL-13 - Clean-machine bootstrap proof

## GOAL

Prepare the next queue item after LOCAL-12 proved explicit read-only LAN smoke.

## WHY

LOCAL-00 through LOCAL-11 established the Local Appliance track, explicit
instance bootstrap, migration guard, runtime composition, localhost service,
HTML workbench, hardened diagnostic pages, durable WorkUnit queue,
operator-gated local review/rebuild, deterministic local workers, and the
measurable auto-test/search harness, plus an explicit read-only LAN safety gate.

LOCAL-13 is now recommended to prove clean-machine bootstrap under an explicit
future task prompt.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-13/task.yaml`
- `runtime/local_network/`
- `scripts/eureka_lan_smoke.py`
- `scripts/validate_local_lan_smoke.py`
- `runtime/local_eval/`
- `runtime/local_service/`
- `runtime/local_workbench/`
- `runtime/local_worker/`
- `control/inventory/local_12_next_task_decision.json`
- `control/audits/local-12-lan-read-only-smoke-v0/`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-13 paths must come from a reviewed LOCAL-13 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-12/task.yaml`
- LOCAL-13 docs, tests, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- runtime, contracts, surfaces, site, native, crates, examples, and private local files unless a reviewed LOCAL-13 prompt explicitly allows the path.

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-13 task branch from `dev`.
- Use the LOCAL-10 harness as safety evidence before enabling any LAN behavior.
- Use the LOCAL-12 LAN smoke evidence before clean-machine proof.
- Do not deploy.
- Do not run source probes, extraction, model/provider calls, or unsafe worker kinds unless a future prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-13 focused validator and tests when defined
- `python scripts/validate_local_auto_test_harness.py`
- `python scripts/validate_local_worker_runner.py`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No LAN mutation.
- No deployment.
- No source probe execution.
- No extraction execution.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-13 acceptance criteria must come from a future reviewed LOCAL-13 prompt.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- packet_type: compact_task_packet
- estimated_tokens: 760
- budget_status: PASS
