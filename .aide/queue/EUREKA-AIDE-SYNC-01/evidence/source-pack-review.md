# Q32 Source Pack Review

- Source pack path:
  `C:/Inbox/Git Repos/aide/.aide/export/aide-lite-pack-v0`
- Source repo: `julesc013/aide`
- Source manifest commit:
  `62d13ad7179581f6c46e0ba9c1b3b75567596aa1`
- Source dirty state in manifest: `true`
- Source `pack-status`: PASS; checksums valid, provenance
  `DIRTY_SOURCE_RECORDED`, boundary PASS, 0 checksum/provenance/boundary
  problems.
- Included file count: 194.
- Checksum count: 197.
- Governance classes present:
  - commit message policy, hook, template, and commit checker support
  - changelog preview support
  - task resumption, WorkUnit, and recovery policy
  - generic Git workflow, branch roles, promotion, sync, and prune policy
  - dry-run Git helper policy and commands
  - Q31 inclusion/exclusion golden tasks and portable docs
- Excluded source-state classes:
  source queue/history, source memory, generated context/reports/status,
  source Git detection/helper plans, source changelog previews, `.aide.local/`,
  secrets, raw prompts, and raw responses.

## Import Dry-Run

- Command: `py -3 ..\aide\.aide\scripts\aide_lite.py import-pack --pack
  ..\aide\.aide\export\aide-lite-pack-v0 --target . --dry-run --mode safe`
- Result: WARN/blocked for direct application because the dry-run found 24
  conflicts, 13 broad-root skips, and 0 writes.
- Planned safe copies include new generic Git policy/helper docs, new Q31
  golden tasks, WorkUnit recovery policy, changelog support, and portable docs.
- Conflicts include target-local files such as `AGENTS.md`, commit/task
  governance, `aide_lite.py`, golden-task catalog/tests, memory templates, and
  command catalog.
- Broad roots skipped: source `core/gateway/**` and `core/providers/**`, as
  expected for safe mode.

## Suitability

The pack is suitable for targeted Eureka sync. Direct import is not applied
because target-local conflicts require preservation and selective merge.
