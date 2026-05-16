# Q32 Sync Report

## Source

- Source pack: `C:/Inbox/Git Repos/aide/.aide/export/aide-lite-pack-v0`
- Source commit in manifest:
  `62d13ad7179581f6c46e0ba9c1b3b75567596aa1`
- Source dirty state recorded: `true`
- Source pack status: PASS.

## Method

The source importer dry-run found target conflicts, so Q32 used a targeted
sync instead of applying the full import operation. The sync copied portable
governance files and merged target-specific script/catalog behavior where
needed.

## Updated Portable Governance

- Commit discipline: policy, hook template, commit template, checker command,
  changelog preview command, standard report, tests, and golden tasks.
- Task/WorkUnit recovery: task-resumption, WorkUnit, recovery policies, task
  command family, standard reports, tests, and golden tasks.
- Git workflow: generic workflow, branch roles, promotion, sync, prune, helper
  policies, project profiles, detection/helper command family, tests, and
  golden tasks.
- AIDE Lite command surface: canonical Q31 command support plus preserved
  Eureka-specific golden-task runners.
- Reference docs: portable governance docs copied into `docs/reference/`.

## Preserved Target State

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- Existing `.aide/queue/EUREKA-AIDE-*` history and evidence.
- Eureka-specific golden tasks and architecture-boundary checks.
- Eureka `AGENTS.md` manual product-boundary content outside managed sections.
- Product source paths under `runtime/**`, `contracts/**`, `surfaces/**`,
  `site/**`, `native/**`, `crates/**`, and related product roots.

## Excluded Source State

- AIDE source `.aide/queue/**`
- AIDE source `.aide/memory/**`
- AIDE source generated context, reports, status outputs, and source Git
  detection/helper plans.
- AIDE source changelog previews as target truth.
- `.aide.local/**`, `.env`, secrets, raw prompts, and raw responses.
- Broad source roots such as `core/gateway/**` and `core/providers/**`.

## Conflicts And Skips

Direct dry-run import reported 24 conflicts and 13 broad-root skips. Conflicts
were resolved by preserving target-specific state and applying only portable
canonical governance files. No destructive overwrite of manual target content
was performed.
