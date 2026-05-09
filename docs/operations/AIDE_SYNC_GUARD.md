# AIDE Sync Guard

`scripts/check_git_task_state.py` is a non-mutating preflight for Codex/AIDE Git work. It inspects local Git state and exits nonzero only for FAIL conditions, unless `--fail-on-warn` is used.

The guard does not fetch, merge, push, create branches, clean files, reset history, call networks, or call model/provider APIs. Fetching is an explicit operator step.

## Modes

- `start-task`: use before normal task work.
- `finish-task`: use before committing or pushing a completed task branch.
- `merge-task`: use on the integration machine while merging a task branch into `main`.
- `rescue`: use when dirty/interrupted state exists and feature work must stop.

## Checks

- clean working tree
- no merge state
- no rebase state
- no cherry-pick state
- no revert state
- normal task work is not on `main`
- local `main` is current with `origin/main`
- task branch upstream status
- branch is not behind upstream
- no unpushed `main` work
- expected `origin/main` has not changed unexpectedly
- no forbidden private paths
- no untracked secret-like paths

## Examples

```powershell
python scripts/check_git_task_state.py --mode start-task --task-id SYNC-GUARD-01
python scripts/check_git_task_state.py --mode finish-task --task-id SYNC-GUARD-01 --json
python scripts/check_git_task_state.py --mode merge-task --task-id SYNC-GUARD-01 --allow-main
```

Use `--allow-main` only for explicit integration, rescue, or guard exceptions. Use `--allow-no-upstream` for a new task branch before its first push. Use `--expected-origin-main <sha>` to warn if the remote-tracking branch differs from the task packet.

## AIDE Use

AIDE should refuse normal task starts on dirty trees, active merge/rebase/cherry-pick/revert states, stale `main`, or direct `main` task work. It should route the operator to:

- `AIDE-SYNC-01` to finish and push a task branch.
- `AIDE-MERGE-01` to merge a named task branch into `main`.
- `AIDE-RESCUE-01` to preserve dirty work and stop.

WARN-only results are acceptable when documented. FAIL results are stop signs.
