# Validation

## Starting State

- `git status --short`: clean.
- `git branch --show-current`: `main`.
- `git rev-parse HEAD`: `dccfc9c5c97408c4c5fabd877b4caa7d92616813`.
- `git check-ignore .aide.local/`: `.aide.local/`.
- `.aide.local/` directory: absent during inspection.

## Pre-Refresh Eureka AIDE Commands

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS, with review packet path
  warnings from the previous packet.
- `py -3 .aide/scripts/aide_lite.py snapshot`: PASS, wrote
  `.aide/context/repo-snapshot.json` with 4220 files and no inline contents.
- `py -3 .aide/scripts/aide_lite.py index`: PASS, unchanged index artifacts.
- `py -3 .aide/scripts/aide_lite.py context`: PASS, unchanged context packet at
  1808 chars / 452 approximate tokens.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, with 3 warnings and 0 errors
  for optional missing controller/gateway/provider status references.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS, wrote
  `.aide/context/latest-review-packet.md` at 3976 chars / 994 approximate
  tokens with verifier WARN.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS, wrote 15 ledger records;
  one near-budget cache report warning.
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS, summary unchanged.
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS, 6 active golden tasks.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 6/6 golden tasks passed,
  with no provider/model/network calls.
- `py -3 .aide/scripts/aide_lite.py route explain`: PASS, advisory only, no
  provider/model/network calls.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py pack-status`: FAIL because Eureka does not
  contain `.aide/export/aide-lite-pack-v0`; source pack status is checked from
  the source pack path instead.
- `py -3 .aide/scripts/aide_lite.py test`: FAIL in the pre-refresh imported
  pack temp fixture with `NameError: name 'core' is not defined`.
- `py -3 .aide/scripts/aide_lite.py selftest`: FAIL with the same temp fixture
  issue.

## Safe Eureka Validation

- `py -3 scripts/check_architecture_boundaries.py`: PASS, checked 479 Python
  files with no architecture-boundary violations.

## Pending

- Post-refresh AIDE validation.
- Latest handoff packet generation and token estimate.
- `git diff --check`, final status, and targeted secret scan.
