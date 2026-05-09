# Multi-Machine Git Workflow

Eureka now uses a boring Git rule for multi-machine work: `main` is integration only, and each task happens on one named task branch.

This guard exists because the repo previously had local-only Track B work, remote OBS work, stale AIDE context, and an interrupted merge at the same time. The fix is not more elaborate rescue prompts. The fix is a small operating model that prevents the bad state from forming.

## Rules

- Start every task from a clean repository.
- Do not do normal task work directly on `main`.
- Use one branch per task.
- Commit before switching branches.
- Push the task branch when another machine, human, or agent needs to help or
  resume it. Quick single-machine tasks may stay local until merge.
- Merge task branches into `main` from one integration machine only.
- Every merge into local `main` must end by pushing `main` to `origin/main`.
- Other machines should refresh from `origin/main` before starting new work.
- Prune temporary local or remote task branches only after their tip is
  contained in the pushed integration branch.
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
```

For shared work that another machine needs, also run:

```powershell
git push -u origin task/<task-id>
```

`finish-task` may warn that local task commits are not pushed yet. That is a
useful warning for quick local tasks, not a merge instruction.

## Integration Merge

Run this on one integration machine only:

```powershell
python scripts/aide_merge_task_branch_to_main.py --task-id <task-id> --branch task/<task-id> --execute
```

For quick single-machine work, that helper performs this sequence:

```powershell
git fetch origin --prune
python scripts/check_git_task_state.py --mode finish-task --task-id <task-id> --allow-no-upstream
git switch main
git pull --ff-only origin main
python scripts/check_git_task_state.py --mode merge-task --task-id <task-id> --allow-main --fail-on-warn
git merge --no-ff --no-edit task/<task-id>
git diff --check
git push origin main
git fetch origin --prune
python scripts/check_git_task_state.py --mode merge-task --task-id <task-id> --allow-main --fail-on-warn
```

For shared branches, add `--publish-branch`. After `origin/main` contains the
branch tip, add `--delete-merged-branch --delete-remote-branch` to prune with
ancestor checks. The helper uses `git branch -d`, never forced deletion.

If a conflict appears, resolve it immediately or stop. Do not continue feature work in a half-merged state.

## Branch Roles

`main` is the only canonical branch today. Temporary branches may be local-only
for quick work or published for collaboration. Future durable branches such as
`dev`, `nightly`, `alpha`, `beta`, `stable`, `release/*`, or `refactor/*`
should be added through `control/inventory/git/branch_role_policy.json` before
they become shared workflow targets.

The merge helper defaults to `main`, but its target is configurable:

```powershell
python scripts/aide_merge_task_branch_to_main.py --task-id <task-id> --branch task/<task-id> --target-branch <integration-branch> --execute
```

Do not introduce a new target branch by habit. Add the branch role first,
including owner or lane, parent branch, promotion rule, validation gate,
retention, rollback, and cleanup rule.

Nested task branches such as `subtask/<parent>/<child>` or
`agent/<task-id>/<agent-id>` are allowed as future patterns, but they should
merge back into a parent branch or selected integration target only after
validation. Their cleanup rule is the same: delete only after the branch tip is
contained in the pushed parent or integration branch.

## Resync Other Machines

After `origin/main` is pushed, each other machine should run:

```powershell
git fetch origin --prune
git switch main
git pull --ff-only origin main
python scripts/check_git_task_state.py --mode start-task --task-id <next-task-id>
```

The final guard should report that local `main` is current with `origin/main`
and that `main` has no local-only commits before a new task branch starts.

## Dirty Or Interrupted State

If the tree is dirty, or Git is mid-merge/rebase/cherry-pick/revert, stop feature work and use `AIDE-RESCUE-01`. Do not pull, merge, rebase, force-push, reset hard, clean destructively, or stash-pop while the state is unclear.

## PASS / WARN / FAIL

- PASS: safe to continue the selected workflow.
- WARN: continue only after acknowledging the condition, such as a new branch without upstream.
- FAIL: stop. Resolve the Git state before starting or finishing the task.

This workflow changes no Eureka product behavior. It is repository operating discipline only.
