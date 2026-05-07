# Validation

Final command results are recorded after implementation.

- `git status --short`: WARN before commit; scoped AIDE/AGENTS changes are
  present, plus unrelated untracked product-adjacent files under
  `contracts/representations/` and `control/inventory/publication/` that were
  not created or staged by this task.
- `git diff --check`: PASS; PowerShell/git reported expected LF-to-CRLF
  working-tree notices only.
- `py -3 -m unittest discover -s .aide/scripts/tests -p test_golden_tasks.py`:
  PASS; 13 tests.
- `py -3 .aide/scripts/aide_lite.py eval run --task commit_message_standard_golden`:
  PASS; 21/21 checks.
- `py -3 .aide/scripts/aide_lite.py eval run --task task_resumption_standard_golden`:
  PASS; 28/28 checks.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: runs after the
  structured commit is created; result is reported in the final response.
- `py -3 .aide/scripts/aide_lite.py commit check --range 88d437f..HEAD`:
  FAIL before this remediation commit; detects noncompliant published commits
  `78efd5c` and `b3d25ec`.
- `py -3 .aide/scripts/aide_lite.py commit install-hook`: PASS;
  `core.hooksPath` is set to `.aide/hooks` in local Git config.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS; no hard failures.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS; latest task packet is
  4836 chars / 1209 approximate tokens.
- `py -3 .aide/scripts/aide_lite.py test`: PASS; includes commit-message
  selftest coverage.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS; includes commit-message
  selftest coverage.
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS; 14 active tasks.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS; 14/14 tasks passed.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS; latest review packet is
  6248 chars / 1562 approximate tokens.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: WARN/PASS; one existing
  cache report remains near budget and no raw prompt/response storage exists.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN-only; 16 warnings and
  0 errors. Warnings are future `TRACK-A-01` evidence refs, optional AIDE
  status files, current AIDE-governance diff scope, and unrelated untracked
  product-adjacent files.
- `python scripts/check_architecture_boundaries.py`: PASS; checked 479 Python
  files with no violations.
- strict secret scan: PASS after inspection. Matches were false positives from
  `task-packet` path text, local demo `task-run` strings, and literal policy/test
  marker strings such as `sk-ant-`; no actual provider key or private-key block
  was found.
