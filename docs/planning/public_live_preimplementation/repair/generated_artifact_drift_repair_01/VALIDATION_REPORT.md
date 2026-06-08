# Validation Report

## Focused Validation Already Run

| Command | Result |
|---|---|
| `python -m unittest tests.scripts.test_summarize_unittest_log tests.scripts.test_run_full_unittest_discovery` | PASS; 13 tests in 4.918s. |
| Resummarize old external `full_unittest_stdout.txt` / `full_unittest_stderr.txt` with fixed parser | PASS; `contains_forbidden_output_root: false`, `generated_family_count: 0`. |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS; no generated drift paths or forbidden untracked generated outputs. |
| `python scripts/validate_generated_artifact_drift.py --json` | PASS. |
| `python -m unittest tests.operations.test_generated_artifact_drift tests.tools.test_audit_generated_artifact_visibility` | PASS; 9 tests in 0.544s. |
| `python scripts/check_generated_artifact_drift.py --json` | PASS; `status: valid`, 12 artifact groups passed. |

## Final Required Validation

| Command | Result |
|---|---|
| `git diff --check` | PASS; line-ending warnings only for touched files. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS. |
| `python scripts/check_architecture_boundaries.py` | PASS; 921 Python files checked, no violations. |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS; no generated drift paths, forbidden generated outputs, or site/public-index drift. |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS; selected L0 static preflight and L1 focused unit lanes; full discovery deferred. |
| `python scripts/validate_test_lane_policy.py` | PASS; status valid. |
| `python -m unittest tests.operations.test_test_lane_policy tests.scripts.test_eureka_test_select tests.scripts.test_validate_test_lane_policy` | PASS; 6 tests. |

## Full Discovery

Full unittest discovery was not run inside the AI session. It remains an
external gate.

## Recommendation

`PASS_WITH_WARNINGS`
