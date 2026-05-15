# Validation

Commands run before commit:

- `git diff --check`
- LOCAL-04 JSON syntax checks: pass
- `python scripts/validate_local_http_service.py`: pass with pre-existing leakage warnings
- focused LOCAL-04 tests: pass
- manual ignored `./eureka-instance` smoke on `127.0.0.1:8765`: pass
- `python scripts/validate_local_runtime_composition.py`: pass with pre-existing leakage warnings
- `python scripts/check_architecture_boundaries.py`: pass
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: fails before commit because the LOCAL-04 audit pack is newly added generated audit evidence; expected to pass after commit on a clean tree
- `python scripts/audit_runtime_architecture_leakage.py --check --json`: fails with the pre-existing 1030 findings baseline
- `python scripts/validate_runtime_architecture_leakage.py`: fails with the same pre-existing leakage baseline

Commands run after commit:

- `py -3 .aide/scripts/aide_lite.py commit check --latest`: pass
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass
- `python scripts/validate_local_instance_migration_guard.py`: pass with pre-existing leakage warning
- `python scripts/validate_local_instance_bootstrap.py`: pass with pre-existing leakage warning
- `python scripts/validate_local_appliance_track.py`: pass with dev-ahead-main warning
- `python scripts/validate_local_http_service.py`: pass with pre-existing leakage warnings
- `python scripts/validate_local_runtime_composition.py`: pass with pre-existing leakage warnings
- `python scripts/check_architecture_boundaries.py`: pass
- `python scripts/audit_runtime_architecture_leakage.py --check --json`: fails with the pre-existing 1030 findings baseline
- `python scripts/validate_runtime_architecture_leakage.py`: fails with the same pre-existing leakage baseline
- `python -m unittest discover -s tests -t .`: fails with 4146 tests, 3 failures, and 5 errors. Failure headers are in existing runtime leakage/remediation, IA readiness polish, public search index builder, generated artifact drift, and public search index validation lanes.

Known warning: the runtime leakage gate has pre-existing findings outside LOCAL-04.
