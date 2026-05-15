# AIDE Latest Task Packet

## PHASE

HUNT-09 - Agent research task contract, provider disabled

## GOAL

Use the HUNT-08 workbench integration smoke as the starting point for the next reviewed task. HUNT-09 is queued and providers remain disabled.

## CURRENT STATE

- Latest completed item: HUNT-08 - Workbench hunt integration and smoke tests.
- Current recommended item: HUNT-09 - Agent research task contract, provider disabled.
- Alternative next item: SYN-00 - Synthetic Query Foundry planning over Local Appliance.
- F0 remains deferred unless explicitly selected by the operator.

## IMPLEMENTED

- Durable Search Hunt Sessions.
- Search Hunt UI state.
- Operator-gated Search Hunt commands and steering.
- Deterministic local/current-index exhaustion reports.
- Durable local SearchNeeds created from hunts and linked exhaustion reports.
- SearchNeed-to-WorkUnit plan generation and local WorkUnit creation.
- Background hunt runner over deterministic local workers.
- End-to-end local Search Hunt workflow smoke through CLI/API/workbench.

## BOUNDARIES

- HUNT-08 runs only deterministic local workers allowed by LOCAL-09 policy.
- No source probes.
- No extraction runtime.
- No AI/model/provider calls.
- No review/master index mutation.
- No deployment.
- No production readiness claim.
- No public launch readiness claim.

## VALIDATION

Use HUNT-08 evidence before starting HUNT-09:

- `python scripts/validate_search_hunt_workbench_integration.py`
- `python -m unittest tests.runtime.test_search_hunt_workflow_integration`
- `python -m unittest tests.runtime.test_search_hunt_workbench_integration`
- `python -m unittest tests.runtime.test_search_hunt_api_integration`
- `python -m unittest tests.runtime.test_search_hunt_safety_integration`
- `python -m unittest tests.operations.test_search_hunt_workflow_smoke_scripts`
- `python -m unittest tests.operations.test_search_hunt_workbench_smoke_scripts`

## EVIDENCE

- `control/audits/hunt-08-workbench-integration-smoke-v0/README.md`
- `control/audits/hunt-08-workbench-integration-smoke-v0/hunt_08_report.json`
- `control/inventory/search_hunt_workbench_integration_result.json`
- `control/inventory/search_hunt_workflow_smoke_result.json`
- `control/inventory/hunt_08_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

HUNT-08 did not implement source probes, extraction, SYN, F0, AI escalation, deployment, production readiness, or public launch readiness.
