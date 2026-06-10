# Multi-Commit Policy

Long turns may commit more than once, but each commit must describe one
coherent completed unit. The goal is recoverability and reviewability, not a
large pile of partial checkpoints.

## Cadence

Commit after each unit that is:

- complete against its acceptance criteria;
- validated with the lane that fits its risk;
- internally coherent if the turn stops immediately after it;
- limited to related files.

Do not commit while the work is knowingly half-applied unless the commit is an
explicit handoff artifact that says what is incomplete.

## Separation

Prefer separate commits for:

- docs, runbooks, and planning packages;
- validator or script repair;
- tests or fixtures;
- runtime behavior;
- generated artifacts.

Combine files only when the task is naturally atomic, such as a documentation
package whose files depend on each other.

## Staging Rules

Before each commit:

```powershell
git status --short
git diff --check
```

Stage only files related to the completed unit. Do not stage unrelated dirty
files. If unrelated files are already dirty, stop and report unless the user has
explicitly asked to continue around them and the paths are clearly separable.

## Commit Messages

Use conventional scoped subjects where practical:

```text
docs(prompt): add long-turn operating protocol
docs(queue): update artifact evidence handoff
docs(validation): record source snapshot ingest
test(eval): add hard-query guard
fix(validation): repair generated artifact drift check
feat(surface): add bounded public-safe projection
```

For substantive work, include a structured Markdown body:

```text
Summary:
- ...

Validation:
- ...

Boundaries:
- no runtime behavior change
- public alpha remains blocked
- dev -> main remains blocked
```

## Commit Check

After every commit when practical:

```powershell
py -3 .aide/scripts/aide_lite.py commit check --latest
```

If commit check fails, do not continue into the next task until the failure is
understood, fixed, or explicitly reported as a blocker.

## Push And Sync

Do not mutate branches, push, force-push, or promote without explicit
authorization or a repo-approved helper plan. A final report may recommend a
push when local `dev` is ahead of `origin/dev`, but recommendation is not
permission to push.
