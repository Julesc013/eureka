# Q55 Readiness

## Status

`READY_FOR_Q55_WITH_WARNINGS`

## Decision

Q55 is ready as a local-only upgrade/dry-run phase from the stable bundle, provided it honors the warnings below. It should not be a fresh install.

## Source Bundle

- Use: `C:/Inbox/Git Repos/aide/.aide/release/dist/`
- Preferred archive: `aide-lite-pack-v0.zip`
- Acceptable alternate archive: `aide-lite-pack-v0.tar.gz`
- Bundle id: `aide-lite-pack-v0-2b2a00f7c4628311`
- Checksum status: PASS.

## Warnings / Non-Blocking Preconditions

- Local `dev` is ahead 9 and behind 6 relative to `origin/dev`; Q55 must remain local-only and must not push.
- Remote `origin/dev` is actively moving with HUNT work; Q55 must re-check divergence before any later publish.
- Pre-existing untracked `native/win/winforms/src/Eureka/obj/` must be classified, ignored, or cleaned by an explicit safe workflow before final promotion.
- Existing gateway/provider AIDE status subcommands fail in this target import and should be repaired by portable report-only upgrade logic.
- Source bundle is local preview with `no_publish: true`, not an official published release.

## Allowed Q55 Paths

Q55 should restrict writes to reviewed AIDE upgrade surfaces, for example:

- `.aide/scripts/**`;
- `.aide/policies/**`;
- `.aide/evals/golden-tasks/**`;
- `.aide/adapters/**`;
- `.aide/generated/adapters/**`;
- `.aide/git/**`;
- `.aide/changelog/**`;
- `.aide/context/**` generated packets;
- `.aide/queue/EUREKA-AIDE-UPGRADE-*/**`;
- `.aide/reports/eureka-*upgrade*`;
- `.aide/reports/eureka-*tool*`;
- `.aide/reports/eureka-*preservation*`;
- other `.aide/{intent,repo,quality,refactor,roots,tools,install,repair,upgrade,rollback,uninstall,release}/**` surfaces only after compare/plan shows no target-state overwrite.

## Forbidden Q55 Paths

- `runtime/**`, `contracts/**`, `surfaces/**`, `site/**`, `snapshots/**`, `native/**`, `crates/**`, `examples/**`, `evals/**`, `docs/**`, `scripts/**`, `tests/**`, `.github/**`, `.git/**`, `.aide.local/**`, `.env`, `secrets/**`.
- Existing `.aide/memory/**`, `.aide/queue/**`, and target evidence must not be overwritten by source state.

## Required Q55 Validation

- Git guard and `git status --short --branch`.
- `git diff --check`.
- `git check-ignore .aide.local/`.
- AIDE `doctor`, `validate`, `test`, `selftest`, `eval run`, `adapter validate`, `commit check --latest`.
- AIDE upgrade/repair/install planning commands in observe/plan/dry-run mode if present after unpack/compare.
- `scripts/check_architecture_boundaries.py`.
- Targeted secret scan.
- Release bundle checksum/listing validation.

## Q55 Output

- Queue packet and evidence under a Q55 task id.
- Upgrade compare/plan/dry-run report.
- Preservation/absorption conflict report.
- Validation report.
- Commit following AIDE Commit Discipline v0 if safe.
