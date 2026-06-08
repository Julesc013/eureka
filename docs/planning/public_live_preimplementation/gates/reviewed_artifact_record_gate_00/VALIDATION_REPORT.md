# Validation Report

Task: `REVIEWED-ARTIFACT-RECORD-GATE-00`

Status: `PASS_WITH_WARNINGS`

## Results

```text
python -m unittest tests.evals.test_reviewed_artifact_record_gate
status: PASS
tests: 9

git diff --check
status: PASS
note: PowerShell/Git reported expected LF-to-CRLF working-copy warnings for .aide files only.

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

Full discovery status:

```text
not run inside AI
previous external full discovery green at 0567f1db7dd28a095eade3db16fb8751a1a68e6f
green_at_prior_head_but_stale_after_this_commit
```

Gate status:

```text
public_alpha_artifact_gate: FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS
reviewed_artifact_record_count: 0
verified_artifact_count: 0
next_recommended_task: MANUAL-ARTIFACT-OBSERVATION-BATCH-00
public alpha: blocked
dev -> main promotion: blocked
```
