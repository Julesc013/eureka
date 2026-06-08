# Validation Report

## Initial Status

Targeted external family:

`unittest-e31dd26eed981165`

Targeted labels:

- `tests.operations.test_local_worker_scripts.LocalWorkerScriptTests.test_validator_passes`
- `tests.runtime.test_source_observation_validation.SourceObservationValidationTests.test_validator_passes_or_warns_for_current_repo`

## Focused Results Already Captured

| Command | Result |
|---|---|
| `python scripts/validate_source_observation_seam.py --json` | PASS; `status: pass`, `forbidden_vocabulary_found: 0`, `h_series_dependencies: 0`, `network_dependencies: 0`. |
| `python tools/validators/validate_ia_live_metadata_probe.py` | PASS; `status: pass`. |
| `python tools/validators/validate_ia_tls_trust.py` | PASS; `status: pass`. |
| `python -m unittest tests.operations.test_local_worker_scripts.LocalWorkerScriptTests.test_validator_passes tests.runtime.test_source_observation_validation.SourceObservationValidationTests.test_validator_passes_or_warns_for_current_repo tests.runtime.test_ia_live_transport` | PASS; 9 tests in 134.935s on final rerun. |

## Final Validation

Final required validation is recorded here before commit:

| Command | Result |
|---|---|
| `git diff --check` | PASS; line-ending warnings only. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS. |
| `python scripts/check_architecture_boundaries.py` | PASS; 921 Python files checked, no architecture-boundary violations. |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS; no generated drift paths or forbidden untracked generated outputs. |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS; selected L0/L1 lanes and skipped full discovery by policy. |
| `python scripts/audit_runtime_architecture_leakage.py --check --json` | PASS_WITH_WARNINGS by known allowlist posture; exit 0, zero blockers and zero new violations. |
| `python scripts/validate_runtime_architecture_leakage.py` | PASS; `status: valid`, `error_count: 0`. |
| `python scripts/validate_test_lane_policy.py` | PASS; `status: valid`, `error_count: 0`. |
| `python -m unittest tests.operations.test_runtime_architecture_leakage tests.operations.test_test_lane_policy tests.scripts.test_eureka_test_select tests.scripts.test_validate_test_lane_policy` | PASS; 26 tests in 138.068s. |

## Full Discovery

Full unittest discovery was not run inside the AI session. A future external
rerun remains required after residual families are repaired or externalized.

## Protected Paths

No protected canon, release, archive zip, reviewed index, public index, or
master index path was modified.

## Recommendation

`PASS_WITH_WARNINGS`
