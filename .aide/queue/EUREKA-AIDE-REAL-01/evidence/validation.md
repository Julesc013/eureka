# Validation

## Baseline

- `git status --short`: PASS, clean before edits.
- `git diff --check`: PASS.
- `git check-ignore .aide.local/`: PASS, `.aide.local/` is ignored.
- `python scripts/check_architecture_boundaries.py`: PASS, 479 Python files
  checked with no boundary violations.

## AIDE Lite Checks

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN-only, 12 warnings, 0
  errors.
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS, 12 active tasks.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 12/12 tasks.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS, refreshed
  `.aide/context/latest-review-packet.md`, 4,899 chars / 1,225 approximate
  tokens, verifier result WARN.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS, refreshed token
  ledger and summary; one existing near-budget cache-report warning.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.

## Report Checks

- `python -m json.tool .aide/reports/eureka-repo-health.json`: PASS.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`:
  PASS, 4,796 chars / 1,199 approximate tokens, within budget.
- strict provider/private-key scan: PASS after inspection. Matches were false
  positives from `task-packet` path text and literal policy/test marker strings;
  no actual provider key, provider environment assignment, or private-key block
  was found.

## Known WARN-only Conditions

- Optional AIDE controller/gateway/provider status references may be absent.
- Future `EUREKA-CONVERGE-01` evidence references may warn until that task runs.
- During pre-commit validation, `verify` also reports diff-scope warnings while
  current `EUREKA-AIDE-REAL-01` evidence is uncommitted and the active queue
  points to the next task. It remains WARN-only with 0 errors.
