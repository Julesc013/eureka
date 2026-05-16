# Validation Evidence

## Summary

ECHECK validation result: `PASS_WITH_WARNINGS`.

Product-slice behavior and architecture checks pass. Core AIDE validation passes.
Warnings remain for AIDE eval, dirty git state, repo unknown classifications,
release dist absence, missing refactor maps, and one no-output AIDE command
rerun.

## Product Behavior

- Runtime fixture tests: PASS, 12 tests.
- Operation fixture validator tests: PASS, 3 tests.
- Fixture vertical slice validator: PASS.
- Persisted reviewed-index artifact included in the ECHECK fixture report.
- Search/object/absence from persisted index available in report.

## Architecture

- `python scripts/check_architecture_boundaries.py`: PASS, 693 Python files.

## AIDE Core

- doctor: PASS.
- validate: PASS.
- test: PASS.
- selftest: PASS.
- review-pack: PASS.
- intent validate: PASS.
- repo validate: WARN, unknown classifications.
- quality validate: PASS.
- tools validate: PASS by output/prior validation.
- install/repair/upgrade/rollback/uninstall validate: PASS.
- git policy: PASS.
- commit check latest: PASS.

## AIDE Warnings / Failures

- eval run: FAIL/INCOMPLETE. Post-write rerun produced no stdout and
  `LASTEXITCODE=-1`. Latest recorded golden report: 127 pass / 9 fail.
- verify: WARN, diff-scope warnings from cumulative local artifacts.
- quality ledger: FAIL/no stdout in this shell; quality validate/status pass.
- refactor validate-map: FAIL, no current maps.
- release validate/status: FAIL, target-local release dist missing and
  no-publish remains true.
- git plan: blocked by dirty tree, no mutation.

## Git / Local State

- `git diff --check`: PASS with line-ending warnings only.
- `git check-ignore .aide.local/`: PASS.
- Git guard: FAIL/WARN as expected for dirty/diverged tree.

## Commit Status

No ECHECK commit was created because the current worktree contains cumulative
Q56-Q61 local artifacts and product/test files that are not safely separable
from the audit-only checkpoint.
