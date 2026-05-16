# Existing AIDE State

## Presence And Version

- `.aide/` exists.
- Current script: `.aide/scripts/aide_lite.py`
- Current reported version: `aide-lite q24.existing-tool-adapter-compiler.v0`
- Profile import source: `D:/Projects/AIDE/aide/.aide/export/aide-lite-pack-v0`, imported for Q22 on 2026-05-07.

## Current Capabilities

Supported command families from `--help`:

- `doctor`, `validate`, `estimate`, `snapshot`, `index`, `context`, `map`, `pack`, `verify`, `review-pack`, `ledger`, `eval`, `commit`, `changelog`, `task`, `git`, `outcome`, `optimize`, `route`, `cache`, `gateway`, `provider`, `export-pack`, `import-pack`, `pack-status`, `adapter`, `adapt`, `selftest`, `test`, `version`, `show-config`.

Missing from the current target install but present in the stable release bundle as Q36-Q48-era surfaces:

- intent compiler / prompt normalization;
- repo intelligence inventory and maps beyond current context map;
- file quality ledger;
- refactor control plane;
- root recycling framework;
- existing tool absorption framework;
- install, repair, upgrade, rollback, and uninstall planning surfaces.

## Policies And State To Preserve

- Memory: `.aide/memory/project-state.md`, `.aide/memory/decisions.md`, `.aide/memory/open-risks.md`.
- Context packets: `.aide/context/latest-task-packet.md`, `.aide/context/latest-review-packet.md`, context index, repo map, test map, route/cache status.
- Policies: token budget, local state/cache, verification, adapter, gateway, provider adapter, commit discipline, task resumption, WorkUnit recovery, Git workflow, promotion/sync/prune.
- Golden tasks: 31 active tasks in `.aide/evals/golden-tasks/catalog.yaml`.
- Queue state: extensive target queue including EUREKA AIDE phases, LOCAL-00..LOCAL-14, HUNT, SYN, F0, TRACK-A, and other repo task packets.
- Reports: `eureka-*`, token ledger/savings, commit/task-resumption standards, repo-health reports.

## Prior Target-Local Fixes

- Q22 / `EUREKA-AIDE-PILOT-01`: imported AIDE Lite, initialized target packets, and recorded token-savings evidence; status remains `needs_review`.
- Q26 / `EUREKA-AIDE-SELFTEST-01`: repaired temp-fixture fallback so target `test` and `selftest` pass; status remains `needs_review`.
- `EUREKA-AIDE-GOLDEN-01`: added Eureka-specific golden tasks; older status says 12 active tasks passed, current catalog now has 31 active tasks and passes all 31.
- Q32 / `EUREKA-AIDE-SYNC-01`: synced portable Q31 governance while preserving target memory, queue, evidence, golden tasks, and product roots; status remains `needs_review`.
- `EUREKA-AIDE-GOVERNANCE-01`: commit discipline and task resumption are present; status remains `needs_review`.

## Validation Summary

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 31/31.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py git status`: PASS command execution; reports dirty tree.
- `py -3 .aide/scripts/aide_lite.py git plan`: blocked as expected by dirty tree, dry-run only, wrote latest helper plan.
- `py -3 .aide/scripts/aide_lite.py pack-status`: FAIL because target repo does not carry `.aide/export/aide-lite-pack-v0`; this is not the source bundle used by Q54.
- `py -3 .aide/scripts/aide_lite.py gateway status`: FAIL, `ModuleNotFoundError: No module named 'core'`.
- `py -3 .aide/scripts/aide_lite.py provider status`: FAIL, `ModuleNotFoundError: No module named 'core'`.

## Interpretation

Existing AIDE is usable for target governance and validation, but it is not the latest stable pack. Q55 should perform an upgrade, not an install. It must preserve target-specific state and repair/report-only gateway/provider command behavior without importing source repo runtime state as product truth.
