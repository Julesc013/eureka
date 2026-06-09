# Validation Report

Task: `HUMAN-ARTIFACT-REVIEW-BATCH-00`

Status:

```text
PASS_WITH_WARNINGS
```

Required outputs created:

```text
evals/hard_queries/artifact_reviews/batch_00/
evals/hard_queries/reviewed_artifact_records/batch_00/
evals/hard_queries/artifact_record_gate/gate_01/
docs/planning/public_live_preimplementation/implementation/human_artifact_review_batch_00/
```

Truth-boundary posture:

```text
runtime source calls: not performed
downloads: not performed
file fetching: not performed
Wayback replay: not performed
reviewed/public/master index mutation: not performed
public alpha launch: not performed
dev -> main promotion: not performed
```

Validation commands:

```text
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 scripts/eureka_test_select.py --changed --failed-first --json
python -m unittest tests.evals.test_human_artifact_review_batch tests.evals.test_reviewed_artifact_records_batch tests.evals.test_artifact_record_gate_after_human_review tests.runtime.test_surface_artifact_review_projection
python scripts/validate_test_lane_policy.py
python -m unittest tests.operations.test_test_lane_policy
python -m unittest tests.scripts.test_eureka_test_select
python -m unittest tests.scripts.test_validate_test_lane_policy
```

Results:

```text
git diff --check: PASS with LF-to-CRLF working-copy warnings for AIDE files
AIDE doctor: PASS
AIDE validate: PASS
architecture boundaries: PASS, 921 Python files checked
generated artifact cleanliness: pass
changed/failed-first selector: L0_static_preflight and L1_focused_unit selected; full discovery deferred
focused artifact review tests: PASS, 23 tests
test lane policy validation: valid, error_count 0
tests.operations.test_test_lane_policy: PASS, 1 test
tests.scripts.test_eureka_test_select: PASS, 3 tests
tests.scripts.test_validate_test_lane_policy: PASS, 2 tests
```

Warnings:

```text
Full unittest discovery was not run inside the AI session.
The prior green external full-discovery result is green at the prior head but stale after this docs/eval commit.
Public alpha remains blocked.
dev -> main promotion remains blocked.
```
