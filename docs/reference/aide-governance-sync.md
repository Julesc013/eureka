# AIDE Governance Sync

Q32 synced Eureka from the canonical Q31 AIDE Lite Pack. The sync imports
portable governance only; it does not change Eureka product behavior.

## Imported Capabilities

- Structured commit policy, commit template, and local hook template.
- Commit checker and changelog preview commands.
- Task resumption, WorkUnit, and recovery policies.
- Generic Git workflow, branch role, promotion, sync, prune, and helper
  policies.
- Dry-run Git detection and helper commands under `.aide/scripts/aide_lite.py`.
- Portable golden tasks and tests for the imported governance surfaces.

## Preserved Target State

- Eureka memory under `.aide/memory/`.
- Eureka queue and evidence under `.aide/queue/`.
- Eureka-generated context, review, ledger, eval, and Git reports.
- Eureka-specific golden tasks and architecture-boundary checks.
- Manual `AGENTS.md` content and product-source boundaries.

## Excluded Source State

The sync must not import AIDE source queue history, source memory, generated
context/reports, source Git detection outputs, source helper plans,
`.aide.local/`, secrets, raw prompts, raw responses, or product-code roots.

## Local Checks

Use these checks before future AIDE-managed work:

```powershell
py -3 .aide/scripts/aide_lite.py validate
py -3 .aide/scripts/aide_lite.py test
py -3 .aide/scripts/aide_lite.py eval run
py -3 .aide/scripts/aide_lite.py commit check --latest
py -3 .aide/scripts/aide_lite.py task inspect
py -3 .aide/scripts/aide_lite.py git plan
py -3 .aide/scripts/aide_lite.py git policy
```

Git helper commands are dry-run by default. Do not create, merge, promote,
push, or prune branches without an explicit future queue item, validation
evidence, and operator approval.
