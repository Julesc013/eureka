# Guard Status

## Guard Scripts

- `scripts/check_git_task_state.py` exists.
- `scripts/validate_sync_guard_policy.py` exists.

## Guard Result

After the final baseline push, the guard passed on `main` in merge-task mode:

```text
python scripts/check_git_task_state.py --mode merge-task --task-id SYNC-BASELINE-01 --allow-main
status: PASS
```

The start-task guard is also expected to return WARN on `main` even with `--allow-main`;
that is the intentional advisory that normal task work should occur on a task branch.

Checks confirmed:

- clean working tree
- no merge state
- no rebase state
- no cherry-pick state
- no revert state
- local `main` current with `origin/main`
- no unpushed main work
- no secret-like changed or untracked paths

## AIDE Workflow Readiness

Available prompt categories:

- `AIDE-SYNC-01`
- `AIDE-MERGE-01`
- `AIDE-RESCUE-01`
