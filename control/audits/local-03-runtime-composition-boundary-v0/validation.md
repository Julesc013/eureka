# Validation

Validation is recorded in `local_03_report.json` and `generated/sample_validation_result.json`.

Commands run before commit:

- `git diff --check`: pass
- JSON syntax checks for LOCAL-03 policy, inventory, and report files: pass
- `python scripts/validate_local_runtime_composition.py`: pass with pre-existing leakage warning
- manual ignored `./eureka-instance` smoke: pass
- focused LOCAL-03 tests: pass
- `python scripts/check_architecture_boundaries.py`: pass
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass after commit
- `python scripts/audit_runtime_architecture_leakage.py --check`: fails with the pre-existing 1030 findings baseline
- `python scripts/validate_runtime_architecture_leakage.py`: fails with the same pre-existing leakage baseline
- `python scripts/validate_local_instance_migration_guard.py`: pass with pre-existing leakage warning after commit
- `python scripts/validate_local_instance_bootstrap.py`: pass with pre-existing leakage warning after commit
- `python scripts/validate_local_appliance_track.py`: pass with dev-ahead-main warning after commit
- `python -m unittest discover -s tests -t .`: fails with 4128 tests, 3 failures, and 5 errors. Failure headers are in existing runtime leakage/remediation, IA readiness polish, public search index builder, generated artifact drift, and public search index validation lanes.

Expected warning: the pre-existing runtime leakage gate still fails. LOCAL-03 does not increase leakage.
