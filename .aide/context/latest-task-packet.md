# AIDE Latest Task Packet

## PHASE

TEST-LANE-ROUTER-01 - Add test selection, failure ledger, and promotion-grade test policy

## GOAL

Replace ad hoc full unittest discovery before every commit with an explicit test-lane system that is faster, safer, and auditable.

## WHY

WORKBENCH-RESULT-LANES-01 added runtime view-model code and then full discovery found two stale Search Hunt queue-handoff failures. Those failures were patched, but full discovery was intentionally not rerun before this task. The repo now needs a selector and failure ledger so the next closeout can rerun failed-first and impact-selected lanes instead of paying a one-hour blind gate on every small commit.

## BOUNDARIES

- no tests deleted
- no test requirements weakened
- no runtime product behavior change
- no IA live call
- no source probe
- no extraction
- no model/provider call
- no deployment
- no production/public launch claim

## KEY FILES

- `contracts/testing/`
- `control/policies/test_lane_policy.json`
- `control/inventory/test_lane_matrix.json`
- `control/inventory/test_impact_map.json`
- `control/inventory/test_failure_ledger.json`
- `control/inventory/test_selection_result_schema.json`
- `scripts/eureka_test_select.py`
- `scripts/validate_test_lane_policy.py`
- `docs/operations/TEST_LANE_POLICY.md`
- `docs/operations/TEST_SELECTION_RUNBOOK.md`
- `docs/operations/PROMOTION_TEST_POLICY.md`
- `docs/architecture/TEST_AND_VALIDATION_ARCHITECTURE.md`

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/reports/eureka-repo-health.json`
- `control/inventory/tests/command_matrix.json`
- `docs/operations/TEST_AND_EVAL_LANES.md`

## ALLOWED_PATHS

- `contracts/testing/**`
- `control/policies/test_lane_policy.json`
- `control/inventory/test_lane_matrix.json`
- `control/inventory/test_impact_map.json`
- `control/inventory/test_failure_ledger.json`
- `control/inventory/test_selection_result_schema.json`
- `control/inventory/test_lane_router_result.json`
- `control/inventory/test_lane_router_next_task_decision.json`
- `scripts/eureka_test_select.py`
- `scripts/validate_test_lane_policy.py`
- `tests/operations/test_test_lane_policy.py`
- `tests/operations/test_test_impact_map.py`
- `tests/operations/test_test_failure_ledger.py`
- `tests/scripts/test_eureka_test_select.py`
- `tests/scripts/test_validate_test_lane_policy.py`
- `docs/operations/TEST_LANE_POLICY.md`
- `docs/operations/TEST_SELECTION_RUNBOOK.md`
- `docs/operations/PROMOTION_TEST_POLICY.md`
- `docs/architecture/TEST_AND_VALIDATION_ARCHITECTURE.md`
- `.aide/queue/TEST-LANE-ROUTER-01/task.yaml`
- `.aide/queue/TEST-LANE-ROUTER-01/**`
- `.aide/queue/WORKBENCH-RESULT-LANES-CLOSEOUT-01/task.yaml`
- `.aide/queue/WORKBENCH-RESULT-LANES-CLOSEOUT-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/test-lane-router-01-v0/**`

## FORBIDDEN_PATHS

- `runtime/connectors/**`
- `runtime/extraction/**`
- `native/**`
- `crates/**`
- `site/dist/**`
- `data/public_index/**`
- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`

## IMPLEMENTATION

- Add explicit L0/L1/L2/L3/L4 test lane policy.
- Add machine-readable path impact map.
- Add failure ledger with the two fixed-pending-full full-discovery failures from the Workbench result-lane closeout.
- Add selector script for changed-path, failed-first, promotion, and full-suite selection.
- Add validator and focused tests.
- Update AIDE queue state so the next task is WORKBENCH-RESULT-LANES-CLOSEOUT-01.

## VALIDATION LANES

- L0 static/preflight
- L1 focused tests
- L2 selected integration tests
- L3 full discovery, required for promotion/high-risk gates
- L4 promotion/release suite

## VALIDATION

- `git diff --check`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/eureka_test_select.py --promotion --json`
- `python scripts/validate_test_lane_policy.py`
- `python -m unittest tests.operations.test_test_lane_policy`
- `python -m unittest tests.operations.test_test_impact_map`
- `python -m unittest tests.operations.test_test_failure_ledger`
- `python -m unittest tests.scripts.test_eureka_test_select`
- `python -m unittest tests.scripts.test_validate_test_lane_policy`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

## EVIDENCE

- `control/audits/test-lane-router-01-v0/`
- `control/audits/test-lane-router-01-v0/generated/sample_test_selection_result.json`
- `control/audits/test-lane-router-01-v0/generated/sample_failure_ledger.json`

## NON_GOALS

- No weakening or deleting tests.
- No runtime product behavior change.
- No promotion to main.
- No IA live call, source probe, extraction, model/provider call, deployment, or production/public launch claim.

## ACCEPTANCE

- Test lane policy exists.
- Test impact map exists.
- Failure ledger exists.
- Selector exists and changed/failed-first/promotion modes work.
- Validator exists and passes.
- Focused tests pass.
- Full discovery is not required per commit.
- Full discovery remains required for promotion.
- Skip reasons are required.
- Queue points to WORKBENCH-RESULT-LANES-CLOSEOUT-01.

## OUTPUT_SCHEMA

- status: PASS / PASS_WITH_WARNINGS / PARTIAL / BLOCKED / FAIL
- include summary, commits, test lane fields, validation fields, boundaries, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1050
- budget_status: PASS

## NEXT TASK

WORKBENCH-RESULT-LANES-CLOSEOUT-01
