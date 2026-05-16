# Install / Upgrade Decision

## Decision

`UPGRADE_EXISTING_AIDE`

## Basis

- Eureka repo identity confirmed by remote URL, repo root, `AGENTS.md`, and
  product roots.
- `.aide/` exists and contains target-specific memory, queue evidence, reports,
  generated context, golden tasks, policies, and scripts.
- Q54 status is `needs_review` with readiness
  `READY_FOR_Q55_WITH_WARNINGS`.
- Source bundle is present at
  `C:/Inbox/Git Repos/aide/.aide/release/dist/` and Q54 plus Q55 checksum
  validation passed.

## Warnings

- Local `dev` is intentionally ahead of and behind `origin/dev`; no push,
  fetch, merge, rebase, or branch mutation is part of Q55.
- Pre-existing untracked `native/win/winforms/src/Eureka/obj/` remains outside
  Q55 scope.
- Local `main` is behind `origin/main`; Q55 does not mutate `main`.

## Apply Method

Targeted manifest-guided sync from the extracted release archive. Source
memory, queues, generated context, generated reports, release dist archives,
raw prompts/responses, secrets, and local state are excluded. Golden tasks are
merged without deleting Eureka-specific tasks.
