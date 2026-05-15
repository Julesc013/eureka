# AIDE Latest Task Packet

## PHASE

HUNT-10 - Deterministic hunt replay harness

## GOAL

Prepare the next task packet around deterministic replay of the completed local Search Hunt workflow, starting from the HUNT-09 disabled agent research contract evidence.

## WHY

HUNT-09 completed the disabled agent research task contract. The next bounded task is deterministic replay over the local Search Hunt workflow, with providers, browser use, source probes, extraction, deployment, and public launch claims still disabled.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/audits/hunt-09-agent-research-task-contract-v0/`
- `control/inventory/agent_research_task_result.json`
- `control/inventory/agent_research_disabled_boundary_result.json`
- `control/inventory/hunt_09_next_task_decision.json`
- `.aide/queue/index.yaml`

## ALLOWED_PATHS

- HUNT-10 queue, audit, inventory, policy, docs, scripts, tests, and runtime paths from the reviewed HUNT-10 task packet.
- Existing local Search Hunt, SearchNeed, WorkUnit, background runner, local service, local workbench, and local appliance paths needed for deterministic replay.

## FORBIDDEN_PATHS

- `runtime/connectors/**`
- `runtime/local_foundry/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `site/dist/**`
- `native/**`
- `crates/**`
- private local files, provider credentials, and ignored local instances.

## IMPLEMENTATION

- Start from HUNT-09 evidence and queue state.
- Keep replay deterministic and local.
- Reuse existing Search Hunt, SearchNeed, WorkUnit, background runner, CLI/API/workbench smoke surfaces.
- Preserve disabled provider and execution boundaries unless the HUNT-10 packet explicitly permits a deterministic local action.

## ACCEPTANCE

- HUNT-10 queue item is current.
- Replay harness records local deterministic workflow inputs and outputs.
- Provider/model calls remain disabled.
- Source probes, extraction, browser/network execution, deployment, review mutation, public/master index mutation, production readiness, and public launch claims remain absent.
- Validation evidence is written under the HUNT-10 audit/inventory paths.

## VALIDATION

Before starting HUNT-10, use the HUNT-09 evidence lane:

- `python scripts/validate_agent_research_task_contract.py`
- focused `tests.runtime.test_agent_research_*`
- `python -m unittest tests.operations.test_agent_research_scripts`

## EVIDENCE

- `control/audits/hunt-09-agent-research-task-contract-v0/hunt_09_report.json`
- `control/inventory/agent_research_task_result.json`
- `control/inventory/agent_research_disabled_boundary_result.json`
- `control/inventory/hunt_09_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

HUNT-10 prep does not enable provider/model calls, browser calls, source probes, extraction, SYN, F0, deployment, production readiness, or public launch readiness.

## OUTPUT_SCHEMA

Final reports should include status, summary, commits, replay capability fields, boundary fields, validation results, and next-task decision.

## TOKEN_ESTIMATE

Approximately 450 words. Use `.aide/context/latest-context-packet.md` for compact repo references instead of expanding historical HUNT task text.
