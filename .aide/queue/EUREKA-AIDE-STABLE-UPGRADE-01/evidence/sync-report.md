# Sync Report

## Method

Q55 used targeted manifest-guided sync from the validated release archive extracted outside the Eureka repo.

No source install command was allowed to overwrite target state blindly. Source-generated state was excluded.

## Result Counts

- Added files: 420.
- Updated files: 153.
- Skipped files: 6.
- Conflicts requiring manual code adaptation: target-local `aide_lite.py` needed Eureka golden task runners restored and target-safe selftest behavior retained.

## Skipped Paths

- `.aide/evals/golden-tasks/catalog.yaml`: merged instead of overwritten.
- `.aide/memory/decisions.template.md`: skipped to preserve target memory.
- `.aide/memory/open-risks.template.md`: skipped to preserve target memory.
- `.aide/memory/project-state.template.md`: skipped to preserve target memory.
- `.aide/quality/file-quality-ledger.schema.json`: initially skipped by broad generated-output protection, then added explicitly from source because it is a portable schema.
- `.aide/queue/README.template.md`: skipped to preserve target queue/history.

## Source-State Exclusions

- Source `.aide/memory/**`.
- Source `.aide/queue/**`.
- Source `.aide/context/latest-*`.
- Source generated repo/quality/root/tool/install/repair/upgrade/rollback/uninstall/release outputs.
- Source release archives and dist copies.
- `.aide.local/**`, raw prompts, raw responses, secrets, local caches.

## Manual Target-Local Fixes

- Reintroduced Eureka-specific golden task dispatch and runner functions for the six Eureka-only golden tasks.
- Added target-safe selftest fixture stubs so portable selftests do not require copying product `core/` files into Eureka.
- Treated optional Gateway/provider helper modules as WARN rather than hard FAIL when absent from a target repo.
- Added the portable file-quality ledger schema required by `quality validate`.

## Managed Sections

`AGENTS.md` was not modified in Q55. Manual content and existing managed sections remain intact.
