# Single Task Template

Use this template for narrow tasks that should produce one coherent diff and,
when validation passes, one commit.

````text
# <TASK-ID>

Use this prompt from the repository root.

## Goal

<One bounded outcome.>

## Scope

Allowed paths:
- <path>

Forbidden paths:
- runtime behavior unless explicitly listed
- contracts unless explicitly listed
- surfaces unless explicitly listed
- site/dist or generated outputs unless explicitly listed
- `.aide.local/**`, local caches, secrets, raw prompt logs, raw responses

## Required Reading

- `AGENTS.md`
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- <task-specific refs>

## Start Guard

Run:

```powershell
python scripts/check_git_task_state.py --mode start-task --task-id <TASK-ID>
```

Stop if the tree is dirty, a merge/rebase/cherry-pick is active, the branch is
`main`, local `main` is stale, or the guard reports a hard failure.

## Plan

Inspect the relevant files and write a bounded plan before editing.

## Work

- Keep the change inside the named boundary.
- Do not add product claims that are not supported by repo evidence.
- Do not fabricate external evidence, reviewed records, verified artifacts, or
  production readiness.

## Validation

Run the smallest lane that fits the task, usually:

```powershell
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 scripts/eureka_test_select.py --changed --failed-first --json
```

Run focused tests if the selector recommends them.

## Commit

If validation passes, commit the coherent change:

```text
<type(scope): short imperative summary>
```

Use a structured Markdown body for substantive work. Then run:

```powershell
py -3 .aide/scripts/aide_lite.py commit check --latest
```

## Final Report

Report status, changed files, validation, commit hash, current queue, gates,
blocked/deferred items, and the next safe task.
````
