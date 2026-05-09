# Validation

Validation completed for SYNC-GUARD-01.

## Required Commands

- `git status --short` - PASS before work; final clean check runs after commit.
- `git diff --check` - PASS.
- `python -m json.tool control/inventory/git/sync_guard_policy.json` - PASS.
- `python -m json.tool control/inventory/git/task_branch_policy.json` - PASS.
- `python -m json.tool control/inventory/git/sync_workflow_commands.json` - PASS.
- `python -m json.tool control/audits/sync-guard-01-multi-machine-git-guard-v0/sync_guard_01_report.json` - PASS.
- `python scripts/check_git_task_state.py --mode start-task --task-id SYNC-GUARD-01 --allow-main` - pending final clean-tree run after commit; expected WARN because the new task branch has no upstream before first push.
- `python scripts/check_git_task_state.py --mode start-task --task-id SYNC-GUARD-01 --allow-main --json` - pending final clean-tree run after commit; expected WARN because the new task branch has no upstream before first push.
- `python scripts/validate_sync_guard_policy.py` - PASS.
- `python -m unittest tests.operations.test_git_task_state_guard tests.operations.test_sync_guard_policy` - PASS, 14 tests.
- `python scripts/check_architecture_boundaries.py` - PASS, 493 Python files checked.

## Optional Broad Suite

- `python -m unittest discover -s tests -t .` - WARN. The broad suite hit the known branch-sensitive public-alpha rehearsal evidence checks because the current branch is `task/sync-guard-01` while that committed evidence pack records `main`. Targeted SYNC-GUARD tests passed and remain the gate for this control task.

## AIDE Lite

- `py -3 .aide/scripts/aide_lite.py doctor` - PASS.
- `py -3 .aide/scripts/aide_lite.py validate` - PASS.
- `py -3 .aide/scripts/aide_lite.py test` - PASS.
- `py -3 .aide/scripts/aide_lite.py selftest` - PASS.
- `py -3 .aide/scripts/aide_lite.py verify` - WARN, zero errors.
- `py -3 .aide/scripts/aide_lite.py eval list` - PASS.
- `py -3 .aide/scripts/aide_lite.py eval run` - PASS, 14/14.
- `py -3 .aide/scripts/aide_lite.py review-pack` - PASS.
- `py -3 .aide/scripts/aide_lite.py adapter validate` - PASS.
