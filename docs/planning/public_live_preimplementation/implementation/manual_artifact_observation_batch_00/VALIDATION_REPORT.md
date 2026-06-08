# Validation Report

Task: `MANUAL-ARTIFACT-OBSERVATION-BATCH-00`

Status: `PASS_WITH_WARNINGS`

## Results

```text
python -m unittest tests.evals.test_manual_artifact_observation_batch
status: PASS
tests: 5

python -m unittest tests.evals.test_artifact_observation_truth_boundary
status: PASS
tests: 5

python -m unittest tests.runtime.test_surface_artifact_observation_projection
status: PASS
tests: 9

git diff --check
status: PASS
note: Git reported expected LF-to-CRLF working-copy warnings for .aide files.

py -3 .aide/scripts/aide_lite.py doctor
status: PASS

py -3 .aide/scripts/aide_lite.py validate
status: PASS

python scripts/check_architecture_boundaries.py
status: PASS
checked: 921 Python files

python scripts/check_generated_artifact_cleanliness.py --check --json
status: pass

py -3 scripts/eureka_test_select.py --changed --failed-first --json
status: PASS
selected lanes: L0_static_preflight, L1_focused_unit

python scripts/validate_test_lane_policy.py
status: PASS

python -m unittest tests.operations.test_test_lane_policy
status: PASS
tests: 1

python -m unittest tests.scripts.test_eureka_test_select
status: PASS
tests: 3

python -m unittest tests.scripts.test_validate_test_lane_policy
status: PASS
tests: 2
```

Full discovery:

```text
not run inside AI
deferred to external harness before promotion/release gates
```

Gate state:

```text
public_alpha_artifact_gate: FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS
manual_artifact_observation_count: 11
reviewable_artifact_item_count: 10
reviewed_artifact_record_count: 0
verified_artifact_count: 0
next_task: HUMAN-ARTIFACT-REVIEW-BATCH-00
```
