# Resync Instructions

Run these commands on every machine, clone, worktree, VM, IDE checkout, and agent workspace after the final baseline push:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git status --short
python scripts/check_git_task_state.py --mode start-task --task-id <next-task>
```

Expected result:

- `main` matches `origin/main`.
- working tree is clean.
- no active merge/rebase/cherry-pick/revert state exists.
- normal task work should continue from a new named branch, not directly from `main`.

Start new work with:

```bash
git switch -c task/<task-id>
python scripts/check_git_task_state.py --mode start-task --task-id <task-id>
```

Finish task work with:

```bash
git status --short
git diff --check
python scripts/check_git_task_state.py --mode finish-task --task-id <task-id>
git add -A
git commit
git push -u origin task/<task-id>
```
