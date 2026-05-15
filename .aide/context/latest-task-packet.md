# AIDE Latest Task Packet

## PHASE

HUNT-06 - Hunt-to-WorkUnit pipeline

## GOAL

Use the HUNT-05 SearchNeed runtime as the starting point for the next reviewed task. HUNT-06 is queued but not implemented in HUNT-05.

## CURRENT STATE

- Latest completed item: HUNT-05 - Hunt-to-SearchNeed pipeline.
- Current recommended item: HUNT-06 - Hunt-to-WorkUnit pipeline.
- Alternative next item: SYN-00 - Synthetic Query Foundry planning over Local Appliance.
- F0 remains deferred unless explicitly selected by the operator.

## IMPLEMENTED

- Durable Search Hunt Sessions.
- Search Hunt UI state.
- Operator-gated Search Hunt commands and steering.
- Deterministic local/current-index exhaustion reports.
- Durable local SearchNeeds created from hunts and linked exhaustion reports.

## BOUNDARIES

- No source probes.
- No extraction runtime.
- No AI/model/provider calls.
- No review/public/master index mutation from SearchNeeds.
- No deployment.
- No production readiness claim.
- No public launch readiness claim.

## VALIDATION

Run HUNT-05 validators and focused tests before using this packet as evidence:

- `python scripts/validate_hunt_to_search_need.py`
- `python -m unittest tests.runtime.test_search_need_store`
- `python -m unittest tests.runtime.test_search_need_records`
- `python -m unittest tests.runtime.test_search_need_transitions`
- `python -m unittest tests.runtime.test_hunt_to_search_need`
- `python -m unittest tests.runtime.test_search_need_routes`
- `python -m unittest tests.runtime.test_search_need_ui`
- `python -m unittest tests.runtime.test_search_need_auth`
- `python -m unittest tests.operations.test_search_need_scripts`

## EVIDENCE

- `control/audits/hunt-05-hunt-to-search-need-v0/README.md`
- `control/audits/hunt-05-hunt-to-search-need-v0/hunt_05_report.json`
- `control/inventory/search_need_runtime_result.json`
- `control/inventory/hunt_to_search_need_result.json`
- `control/inventory/hunt_05_next_task_decision.json`
- `.aide/queue/index.yaml`

## NON_GOALS

HUNT-05 did not implement HUNT-06 WorkUnit generation, source execution, SYN, F0, AI escalation, deployment, production readiness, or public launch readiness.

## ACCEPTANCE

HUNT-06 may start only from repo-local evidence after HUNT-05 passes or passes with warnings.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 1932
- approx_tokens: 483
- budget_status: PASS
