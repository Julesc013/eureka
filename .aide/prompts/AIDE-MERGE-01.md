# AIDE-MERGE-01 - Merge Named Task Branch Into Main

Use this prompt only on the integration machine.

## Goal

Merge one reviewed task branch into `main`, validate, and push `main` normally
so every other machine can fast-forward from `origin/main`.

## Required Steps

1. Start with a clean tree.
2. Fetch origin.
3. Publish the named task branch only when cross-machine help or handoff is needed.
4. Switch to `main`.
5. Fast-forward local `main` from `origin/main`.
6. Run the merge-task guard with `--fail-on-warn`.
7. Merge the named task branch.
8. Resolve conflicts immediately if any appear.
9. Run validation.
10. Push `main` normally.
11. Fetch origin and rerun the merge-task guard to prove `main` has no local-only commits.

Preferred command:

```powershell
python scripts/aide_merge_task_branch_to_main.py --task-id <task-id> --branch task/<task-id> --execute
```

Use `--target-branch <branch>` only after that branch has an explicit role in
`control/inventory/git/branch_role_policy.json`.

For shared task branches that should be cleaned up after merge:

```powershell
python scripts/aide_merge_task_branch_to_main.py --task-id <task-id> --branch task/<task-id> --execute --publish-branch --delete-merged-branch --delete-remote-branch
```

## Stop Conditions

- Local `main` cannot fast-forward from origin.
- Conflict cannot be resolved intentionally.
- Validation fails.
- Secret-like or private local paths appear.
- `main` has local-only commits after the workflow; that means the final push did not complete.

## Forbidden

- No force push.
- No broad one-side conflict deletion.
- No forced branch deletion. Only use safe merged-branch pruning after the
  branch tip is contained in `origin/main`.
- No history rewrite.
- No product boundary changes unless the task explicitly allows them.
