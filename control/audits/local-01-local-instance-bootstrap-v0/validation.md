# Validation

Validation lane:

- `git status --short`: pass, with intended LOCAL-01 changes and ignored `eureka-instance/`.
- `git diff --check`: pass.
- JSON syntax checks for LOCAL-01 policies and inventories: pass.
- `python scripts/validate_local_instance_bootstrap.py`: pass with warning for the pre-existing leakage gate.
- Manual smoke with ignored `./eureka-instance`: pass.
- Focused LOCAL-01 unittest modules: pass.
- `python scripts/validate_local_appliance_track.py`: pass with warning that `origin/dev` is ahead of `origin/main` after Local Appliance queue work.
- `python scripts/check_architecture_boundaries.py`: pass.
- `python scripts/audit_runtime_architecture_leakage.py --check --json`: fail on the pre-existing 1030 new unallowlisted production findings; LOCAL-01 does not increase the count.
- `python scripts/validate_runtime_architecture_leakage.py`: invalid for the same pre-existing leakage gate.
- `python -m unittest discover -s tests -t .`: ran 4087 tests and fails on the known runtime leakage gate with 3 failures and 5 errors; LOCAL-01 focused tests pass.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass after commit.
