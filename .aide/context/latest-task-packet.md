# AIDE Latest Task Packet

## PHASE

HUNT-11 - Bounded AI escalation gate, disabled by default

## GOAL

Prepare the next task packet around a disabled-by-default AI escalation gate after deterministic Search Hunt replay exists.

## WHY

HUNT-10 completed deterministic local replay for the Search Hunt workflow. The next bounded task is an AI escalation gate that must remain disabled by default until an explicit reviewed gate enables providers.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/audits/hunt-10-deterministic-replay-v0/`
- `control/inventory/hunt_replay_result.json`
- `control/inventory/hunt_replay_step_matrix.json`
- `control/inventory/hunt_replay_blocked_step_matrix.json`
- `control/inventory/hunt_10_next_task_decision.json`
- `.aide/queue/index.yaml`

## ALLOWED_PATHS

- HUNT-11 queue, audit, inventory, policy, docs, scripts, tests, and explicitly scoped runtime paths once a reviewed HUNT-11 task packet is provided.

## FORBIDDEN_PATHS

- `runtime/connectors/**`
- `runtime/local_foundry/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `contracts/**` unless explicitly scoped by HUNT-11
- `surfaces/**`
- `site/**`
- `site/dist/**`
- `native/**`
- `crates/**`
- private local files, provider credentials, and ignored local instances.

## IMPLEMENTATION

- Start from HUNT-10 replay evidence and queue state.
- Keep provider/model calls disabled by default.
- Keep source probes, extraction, browser/network execution, deployment, review mutation, and master-index mutation disabled unless a future reviewed gate explicitly enables a narrow action.

## ACCEPTANCE

- HUNT-11 queue item is current.
- HUNT-10 evidence remains available and replay validation passes.
- Provider/model calls remain disabled until a reviewed HUNT-11 gate says otherwise.
- No production readiness or public launch readiness claim is made.

## VALIDATION

Before starting HUNT-11, use the HUNT-10 evidence lane:

- `python scripts/validate_hunt_replay.py`
- focused `tests.runtime.test_hunt_replay_*`
- `python -m unittest tests.operations.test_hunt_replay_scripts`

## EVIDENCE

- `control/audits/hunt-10-deterministic-replay-v0/hunt_10_report.json`
- `control/inventory/hunt_replay_result.json`
- `control/inventory/hunt_replay_demo_result.json`
- `control/inventory/hunt_10_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

This packet does not enable provider/model calls, browser calls, source probes, extraction, SYN, F0, deployment, production readiness, or public launch readiness.

## OUTPUT_SCHEMA

Final reports should include status, summary, commits, AI gate capability fields, boundary fields, validation results, and next-task decision.

## TOKEN_ESTIMATE

Approximately 430 words. Use `.aide/context/latest-context-packet.md` for compact repo references instead of expanding historical HUNT task text.
