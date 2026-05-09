# Validation Matrix

## Git

- `git status --short` - PASS before audit files.
- `git diff --check` - PASS.
- conflict marker scan with `git grep -n -E "^(<<<<<<<|>>>>>>>)"` - PASS.
- live remote check with `git ls-remote origin refs/heads/main` - PASS, observed `52cad7c` before audit commit.

## Guard And Generated Artifacts

- `python scripts/check_architecture_boundaries.py` - PASS, 493 Python files checked.
- `python scripts/check_generated_artifact_drift.py --json` - PASS, 12 artifact groups passed.
- `python scripts/validate_sync_guard_policy.py` - PASS.
- `python -m unittest tests.operations.test_git_task_state_guard tests.operations.test_sync_guard_policy` - PASS, 14 tests.

## Full Tests

- `python -m unittest discover -s tests -t .` - PASS, 2508 tests.

## AIDE Lite

- `py -3 .aide/scripts/aide_lite.py doctor` - PASS.
- `py -3 .aide/scripts/aide_lite.py validate` - PASS.
- `py -3 .aide/scripts/aide_lite.py test` - PASS.
- `py -3 .aide/scripts/aide_lite.py selftest` - PASS.
- `py -3 .aide/scripts/aide_lite.py verify` - WARN, zero errors.
- `py -3 .aide/scripts/aide_lite.py eval list` - PASS.
- `py -3 .aide/scripts/aide_lite.py eval run` - PASS, 14/14 golden tasks.
- `py -3 .aide/scripts/aide_lite.py review-pack` - PASS.
- `py -3 .aide/scripts/aide_lite.py adapter validate` - PASS.
