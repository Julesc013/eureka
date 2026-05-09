# Multi-Machine Git Workflow

Eureka now uses a boring Git rule for multi-machine work: `main` is integration only, and each task happens on one named task branch.

This guard exists because the repo previously had local-only Track B work, remote OBS work, stale AIDE context, and an interrupted merge at the same time. The fix is not more elaborate rescue prompts. The fix is a small operating model that prevents the bad state from forming.

## Rules

- Start every task from a clean repository.
- Do not do normal task work directly on `main`.
- Use one branch per task.
- Commit before switching branches.
- Push the task branch after each completed task.
- Merge task branches into `main` from one integration machine only.
- Finish conflicts immediately; do not leave a repo mid-merge.
- Do not start Codex/AIDE from stale local `main`.
- Do not hide local-only work across machines.

## Start Work

```powershell
git status --short
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c task/<task-id>
python scripts/check_git_task_state.py --mode start-task --task-id <task-id>
```

Example:

```powershell
git switch -c task/sync-guard-01
python scripts/check_git_task_state.py --mode start-task --task-id SYNC-GUARD-01
```

## Finish Work

```powershell
git status --short
git diff --check
python scripts/check_git_task_state.py --mode finish-task --task-id <task-id>
git add -A
git commit
git push -u origin task/<task-id>
```

`finish-task` may warn that local task commits are not pushed yet. That is a useful warning, not a merge instruction.

## Integration Merge

Run this on one integration machine only:

```powershell
git status --short
git fetch origin
git switch main
git pull --ff-only origin main
git merge --no-ff origin/task/<task-id>
python scripts/check_git_task_state.py --mode merge-task --task-id <task-id> --allow-main
git push origin main
```

If a conflict appears, resolve it immediately or stop. Do not continue feature work in a half-merged state.

## Dirty Or Interrupted State

If the tree is dirty, or Git is mid-merge/rebase/cherry-pick/revert, stop feature work and use `AIDE-RESCUE-01`. Do not pull, merge, rebase, force-push, reset hard, clean destructively, or stash-pop while the state is unclear.

## PASS / WARN / FAIL

- PASS: safe to continue the selected workflow.
- WARN: continue only after acknowledging the condition, such as a new branch without upstream.
- FAIL: stop. Resolve the Git state before starting or finishing the task.

This workflow changes no Eureka product behavior. It is repository operating discipline only.
