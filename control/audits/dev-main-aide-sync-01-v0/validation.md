# Validation

Pre-merge inspection:

- `python scripts/check_git_task_state.py --mode start-task --task-id DEV-MAIN-AIDE-SYNC-01`: PASS with expected warnings for branch-name mismatch and local dev ahead of origin/dev by two commits.
- `git status --short --branch`: clean, `dev...origin/dev [ahead 2]`.
- `git ls-remote origin refs/heads/main refs/heads/dev`: main `73d8e9eb590f43a5554abe35f99345c57d4ec06c`, dev `419db7fbdcf3681676cd85496efec950e511fe81`.

Merge validation run before commit:

- `git diff --check`: PASS.
- `python scripts/check_architecture_boundaries.py`: PASS.
- `python -m unittest discover -s tests/runtime -t . -p test_fixture_source_observation_vertical_slice.py`: PASS.
- `python -m unittest discover -s tests/operations -t . -p test_fixture_source_observation_vertical_slice_script.py`: PASS.
- HUNT targeted validators: PASS.
- `python .aide/scripts/aide_lite.py doctor`: PASS.
- `python .aide/scripts/aide_lite.py validate`: PASS.
- `python .aide/scripts/aide_lite.py test`: PASS.
- `python .aide/scripts/aide_lite.py selftest`: PASS.

Post-commit validation:

- `git status --short --branch`: clean on integration branch.
- `git diff --check`: PASS.
- `python scripts/check_architecture_boundaries.py`: PASS.
- `python -m unittest discover -s tests/runtime -t . -p test_fixture_source_observation_vertical_slice.py`: PASS.
- `python -m unittest discover -s tests/operations -t . -p test_fixture_source_observation_vertical_slice_script.py`: PASS.
- `python .aide/scripts/aide_lite.py doctor`: PASS.
- `python .aide/scripts/aide_lite.py validate`: PASS.
- `python .aide/scripts/aide_lite.py test`: PASS.
- `python .aide/scripts/aide_lite.py selftest`: PASS.
- `python .aide/scripts/aide_lite.py verify`: PASS with 0 warnings and 0 errors.
- `python .aide/scripts/aide_lite.py review-pack`: PASS.
- `python .aide/scripts/aide_lite.py commit check --latest`: PASS.
