# Changed Files

Q55 changed only `.aide/**` tracked files and generated new `.aide/**` files.
No tracked product/source/contract/runtime/site/native files were changed.

## Change Classes

- Portable AIDE control-plane sync: `.aide/scripts/aide_lite.py`, `.aide/policies/**`, `.aide/scripts/tests/**`, `.aide/evals/golden-tasks/**`, `.aide/changelog/**`, `.aide/github/**`, `.aide/install/**`, `.aide/repair/**`, `.aide/upgrade/**`, `.aide/rollback/**`, `.aide/uninstall/**`, `.aide/release/**`, `.aide/repo/**`, `.aide/quality/**`, `.aide/roots/**`, `.aide/tools/**`.
- Eureka-local generated state: `.aide/context/**`, `.aide/reports/**`, `.aide/git/**`, `.aide/evals/runs/**`.
- Q55 evidence packet: `.aide/queue/EUREKA-AIDE-STABLE-UPGRADE-01/**`.

## Explicit Non-Changes

- `AGENTS.md` was not modified.
- `.gitignore` was not modified.
- `contracts/**`, `runtime/**`, `surfaces/**`, `site/**`, `snapshots/**`, `native/**`, `crates/**`, `examples/**`, `evals/**`, `tests/**`, and `scripts/**` tracked files were not modified.
- Pre-existing untracked `native/win/winforms/src/Eureka/obj/` remains untracked and outside Q55 scope.

## Verification

- `git diff --name-only`: tracked changed files outside `.aide/**` = 0.
- `git status --short`: allowed `.aide/**` changes plus pre-existing untracked native build output.
