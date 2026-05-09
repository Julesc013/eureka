# AIDE-SYNC-01 - Finish Current Task And Push Branch

Use this prompt when a task branch is ready to be preserved remotely.

## Goal

Validate, commit, and push the current task branch. Do not merge to `main`.

## Required Steps

1. Run `git status --short`.
2. Run `python scripts/check_git_task_state.py --mode finish-task --task-id <task-id>`.
3. Run task-appropriate validation.
4. Commit with the structured commit standard.
5. Push the current branch normally with upstream if needed.

If the branch is ready to become shared canonical work, continue with
`AIDE-MERGE-01` on the integration machine. Quick single-machine branches can
stay local until merge. Shared branches can be published with `--publish-branch`
and pruned after merge with safe ancestor checks. In both cases the merge
workflow fast-forwards local `main`, merges, validates, pushes `main`, and
verifies local `main` has no unpushed commits.

## Stop Conditions

- Dirty paths outside the task scope.
- Active merge, rebase, cherry-pick, or revert state.
- Secret-like or private local paths.
- Validation failure that is not explicitly documented as WARN-only.

## Forbidden

- No merge to `main`.
- No force push.
- No branch deletion.
- No history rewrite.
- No destructive cleanup.
