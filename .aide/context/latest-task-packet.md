# AIDE Latest Task Packet

## PHASE

LOCAL-14 - Local appliance closeout and F0/HUNT/SYN handoff

## GOAL

Prepare the next queue item after LOCAL-13 proved clean-machine bootstrap.

## WHY

LOCAL-00 through LOCAL-13 now establish the Local Appliance track, explicit
instance bootstrap, migration guard, runtime composition, localhost service,
HTML workbench, hardened diagnostic pages, durable WorkUnit queue,
operator-gated review/rebuild, deterministic local workers, auto-test/search,
LAN safety/smoke, and clean-machine reproducibility proof.

LOCAL-14 is recommended to close out the Local Appliance track and hand off to
future F0/HUNT/SYN work without starting those tracks in LOCAL-13.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-14/task.yaml`
- `control/audits/local-13-clean-machine-bootstrap-v0/`
- `control/inventory/local_13_next_task_decision.json`
- `docs/operations/LOCAL_APPLIANCE_REPRODUCIBILITY.md`
- `AGENTS.md`

## ALLOWED_PATHS

- LOCAL-14 paths must come from a reviewed LOCAL-14 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-14/task.yaml`
- LOCAL-14 docs, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- private local files

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-14 task branch.
- Do not deploy.
- Do not start F0 until a reviewed LOCAL-14 prompt allows the closeout handoff.
- Do not run source probes, extraction, model/provider calls, or unsafe worker kinds unless a future prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-14 focused validator and tests when defined
- existing LOCAL validators as scoped
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No deployment.
- No production readiness claim.
- No public launch readiness claim.
- No unscoped F0 implementation.
- No source probe execution.

## ACCEPTANCE

- LOCAL-14 acceptance criteria must come from a future reviewed LOCAL-14 prompt.
- F0 remains deferred until LOCAL-14 closeout decisions are explicit.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- packet_type: compact_task_packet
- estimated_tokens: 720
- budget_status: PASS
