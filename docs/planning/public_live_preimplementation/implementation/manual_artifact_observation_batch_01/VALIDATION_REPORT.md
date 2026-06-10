# Validation Report

Task: `MANUAL-ARTIFACT-OBSERVATION-BATCH-01`

Status: `PASS_WITH_WARNINGS`

## Results

```text
python -m unittest tests.evals.test_manual_artifact_observation_batch_01
status: PASS
tests: 6

python -m unittest tests.runtime.test_surface_artifact_observation_batch_01_projection
status: PASS
tests: 7

python -m unittest tests.evals.test_artifact_observation_truth_boundary tests.evals.test_manual_artifact_observation_batch tests.runtime.test_surface_artifact_observation_projection
status: PASS
tests: 19

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

py -3 .aide/scripts/aide_lite.py pack --task "HUMAN-ARTIFACT-REVIEW-BATCH-01"
status: PASS
path: .aide/context/latest-task-packet.md
approx_tokens: 1195

py -3 scripts/eureka_test_select.py --changed --failed-first --json
status: PASS
selected lanes: L0_static_preflight, L1_focused_unit

python scripts/validate_test_lane_policy.py
status: PASS

python -m unittest tests.operations.test_test_lane_policy tests.scripts.test_eureka_test_select tests.scripts.test_validate_test_lane_policy
status: PASS
tests: 6
```

## Full Discovery

```text
not run inside AI
deferred to external harness before promotion/release gates
```

## Gate State

```text
public_alpha_artifact_gate: FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS
manual_artifact_observation_count: 7
reviewable_artifact_item_count: 6
reviewed_artifact_record_count: 2
new_reviewed_artifact_record_count: 0
verified_artifact_count: 0
next_task: HUMAN-ARTIFACT-REVIEW-BATCH-01
```

Warnings are gate warnings, not focused-validation failures:

- public alpha remains blocked
- `dev -> main` remains blocked
- prior external full-discovery evidence is stale after this docs/eval commit
