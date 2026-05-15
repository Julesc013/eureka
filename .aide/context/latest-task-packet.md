# AIDE Latest Task Packet

## PHASE

HUNT-08 - Workbench hunt integration and smoke tests

## GOAL

Use the HUNT-07 background hunt runner as the starting point for the next reviewed task. HUNT-08 is queued but not implemented in HUNT-07.

## CURRENT STATE

- Latest completed item: HUNT-07 - Background hunt runner over deterministic local workers.
- Current recommended item: HUNT-08 - Workbench hunt integration and smoke tests.
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

## BOUNDARIES

- HUNT-07 runs only deterministic local workers allowed by LOCAL-09 policy.
- No source probes.
- No extraction runtime.
- No AI/model/provider calls.
- No review/master index mutation.
- No deployment.
- No production readiness claim.
- No public launch readiness claim.

## VALIDATION

Use HUNT-07 evidence before starting HUNT-08:

- `python scripts/validate_background_hunt_runner.py`
- `python -m unittest tests.runtime.test_background_hunt_runner_plan`
- `python -m unittest tests.runtime.test_background_hunt_runner_execution`
- `python -m unittest tests.runtime.test_background_hunt_runner_policy`
- `python -m unittest tests.runtime.test_background_hunt_runner_routes`
- `python -m unittest tests.runtime.test_background_hunt_runner_ui`
- `python -m unittest tests.runtime.test_background_hunt_runner_auth`
- `python -m unittest tests.operations.test_background_hunt_runner_scripts`

## EVIDENCE

- `control/audits/hunt-07-background-hunt-runner-v0/README.md`
- `control/audits/hunt-07-background-hunt-runner-v0/hunt_07_report.json`
- `control/inventory/background_hunt_runner_result.json`
- `control/inventory/background_hunt_worker_matrix.json`
- `control/inventory/hunt_07_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

HUNT-07 did not implement source probes, extraction, SYN, F0, AI escalation, deployment, production readiness, or public launch readiness.
