# AIDE Latest Task Packet

## PHASE

HUNT-12 - Search Hunt closeout and SYN/F0 handoff

## GOAL

Prepare the next task packet around Search Hunt closeout and handoff after the disabled AI escalation gate exists.

## WHY

HUNT-11 completed the bounded AI escalation gate with providers disabled by default. The next bounded task is Search Hunt closeout and SYN/F0 handoff without enabling providers, source probes, extraction, or deployment.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/audits/hunt-11-ai-escalation-gate-v0/`
- `control/inventory/ai_escalation_gate_result.json`
- `control/inventory/ai_escalation_disabled_boundary_result.json`
- `control/inventory/hunt_11_next_task_decision.json`
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

- HUNT-12 queue item is current.
- HUNT-11 evidence remains available and AI escalation validation passes.
- Provider/model calls remain disabled until a later reviewed gate says otherwise.
- No production readiness or public launch readiness claim is made.

## VALIDATION

Before starting HUNT-12, use the HUNT-11 evidence lane:

- `python scripts/validate_ai_escalation_gate.py`
- focused `tests.runtime.test_ai_escalation_*`
- `python -m unittest tests.operations.test_ai_escalation_scripts`

## EVIDENCE

- `control/audits/hunt-11-ai-escalation-gate-v0/hunt_11_report.json`
- `control/inventory/ai_escalation_gate_result.json`
- `control/inventory/ai_escalation_demo_result.json`
- `control/inventory/hunt_11_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

This packet does not enable provider/model calls, browser calls, source probes, extraction, SYN, F0, deployment, production readiness, or public launch readiness.

## OUTPUT_SCHEMA

Final reports should include status, summary, commits, AI gate capability fields, boundary fields, validation results, and next-task decision.

## TOKEN_ESTIMATE

Approximately 430 words. Use `.aide/context/latest-context-packet.md` for compact repo references instead of expanding historical HUNT task text.
