# AIDE Latest Task Packet

## PHASE

HUNT-07 - Background hunt runner over deterministic local workers

## GOAL

Use the HUNT-06 Hunt-to-WorkUnit pipeline as the starting point for the next reviewed task. HUNT-07 is queued but not implemented in HUNT-06.

## CURRENT STATE

- Latest completed item: HUNT-06 - Hunt-to-WorkUnit pipeline.
- Current recommended item: HUNT-07 - Background hunt runner over deterministic local workers.
- Alternative next item: SYN-00 - Synthetic Query Foundry planning over Local Appliance.
- F0 remains deferred unless explicitly selected by the operator.

## IMPLEMENTED

- Durable Search Hunt Sessions.
- Search Hunt UI state.
- Operator-gated Search Hunt commands and steering.
- Deterministic local/current-index exhaustion reports.
- Durable local SearchNeeds created from hunts and linked exhaustion reports.
- SearchNeed-to-WorkUnit plan generation and local WorkUnit creation.

## BOUNDARIES

- HUNT-06 creates WorkUnit queue records only.
- No WorkUnit execution.
- No source probes.
- No extraction runtime.
- No AI/model/provider calls.
- No review/public/master index mutation.
- No deployment.
- No production readiness claim.
- No public launch readiness claim.

## VALIDATION

Use HUNT-06 evidence before starting HUNT-07:

- `python scripts/validate_hunt_to_workunits.py`
- `python -m unittest tests.runtime.test_need_to_workunit_plan`
- `python -m unittest tests.runtime.test_need_to_workunit_creation`
- `python -m unittest tests.runtime.test_need_workunit_links`
- `python -m unittest tests.runtime.test_need_workunit_routes`
- `python -m unittest tests.runtime.test_need_workunit_ui`
- `python -m unittest tests.runtime.test_need_workunit_auth`
- `python -m unittest tests.operations.test_need_to_workunit_scripts`

## EVIDENCE

- `control/audits/hunt-06-hunt-to-workunit-v0/README.md`
- `control/audits/hunt-06-hunt-to-workunit-v0/hunt_06_report.json`
- `control/inventory/hunt_to_workunit_result.json`
- `control/inventory/search_need_workunit_link_result.json`
- `control/inventory/hunt_06_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

HUNT-06 did not implement HUNT-07 background running, source execution, SYN, F0, AI escalation, deployment, production readiness, or public launch readiness.
