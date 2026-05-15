# Commands Run

## Repo / Git

- `git status --short`: WARN, dirty tree with cumulative Q56-Q61 local files and
  ECHECK artifacts.
- `git branch --show-current`: PASS, `dev`.
- `git branch --all`: PASS.
- `git remote -v`: PASS, origin `https://github.com/Julesc013/eureka.git`.
- `git rev-parse HEAD`: PASS, `df6a6967afdb510de46651f70e21541f20b6741b`.
- `git rev-parse --show-toplevel`: PASS, `C:/Inbox/Git Repos/eureka`.
- `git log --oneline --decorate -100`: PASS.
- `git tag --list`: PASS, no tags listed.
- `git diff --check`: PASS with line-ending warnings only.
- `git check-ignore .aide.local/`: PASS.
- `python scripts/check_git_task_state.py --mode start-task --task-id ECHECK-01-eureka-source-slice-product-proof-audit`: FAIL/WARN because dirty tree and branch divergence block normal product work.

## Product Slice

- `python -m unittest discover -s tests/runtime -t . -p test_fixture_source_observation_vertical_slice.py`: PASS, 12 tests.
- `python -m unittest discover -s tests/operations -t . -p test_fixture_source_observation_vertical_slice_script.py`: PASS, 3 tests.
- `python scripts/validate_fixture_source_observation_vertical_slice.py --output-root .aide/queue/ECHECK-01-eureka-source-slice-product-proof-audit/evidence/fixture-run --output .aide/queue/ECHECK-01-eureka-source-slice-product-proof-audit/evidence/product-slice-run-report.json --json`: PASS.
- `python scripts/check_architecture_boundaries.py`: PASS, 693 Python files.

## AIDE

- `doctor`: PASS.
- `validate`: PASS.
- `test`: PASS.
- `selftest`: PASS.
- `eval run`: FAIL/INCOMPLETE in current shell; post-write rerun produced no stdout and `LASTEXITCODE=-1`. Prior latest report records 127 pass / 9 fail.
- `verify`: WARN, no errors, dirty diff-scope warnings.
- `review-pack`: PASS.
- `ledger scan`: PASS with token budget warnings.
- `ledger report`: PASS.
- `intent validate`: PASS.
- `intent compile --prompt "Plan the next bounded Eureka product task from ECHECK-01 evidence"`: PASS, compile-only, no execution.
- `intent status`: PASS.
- `repo inventory`: PASS.
- `repo validate`: WARN for unknown classifications.
- `repo status`: PASS.
- `quality validate`: PASS.
- `quality status`: PASS.
- `quality ledger`: FAIL/no stdout in this shell.
- `refactor status`: PASS.
- `refactor validate`: PASS.
- `refactor map-status`: MISSING.
- `refactor validate-map`: FAIL, current maps missing.
- `roots inventory`: PASS.
- `roots validate`: PASS.
- `roots status`: PASS.
- `tools inventory`: output-limited/no stdout in one rerun; existing outputs present.
- `tools validate`: PASS by output and prior validation.
- `tools status`: PASS.
- `tools capabilities`: PASS.
- `install validate`: PASS.
- `repair validate`: PASS.
- `upgrade validate`: PASS.
- `rollback validate`: PASS.
- `uninstall validate`: PASS.
- `commit check --latest`: PASS.
- `changelog preview`: PASS.
- `changelog validate`: PASS.
- `changelog status`: PASS.
- `task inspect`: WARN/exit 1 for shorthand `Q62` missing.
- `task status`: PASS.
- `task noop-check`: PASS, no mutation.
- `git detect`: PASS.
- `git doctor`: PASS command, unsafe for normal task due dirty tree.
- `git status`: PASS command, dirty tree.
- `git policy`: PASS.
- `git plan`: BLOCKED by dirty tree, no mutation.
- `release validate`: FAIL because target release dist artifacts missing.
- `release status`: FAIL/missing bundle.

## Skipped Commands

- `git sync --dry-run`, `git land --dry-run`, and `git promote --dry-run`: skipped
  to avoid any remote/network/branch-sensitive behavior during ECHECK.
- GitHub advisory/validate commands: skipped to avoid GitHub/API/network
  ambiguity.

## Optional Read-Only Sibling Inspection

- `../aide`: present, branch `main`, HEAD
  `dab004e322cac8aec41e7d41787c8482a97f4ae9`; release manifest present and
  records bundle `aide-lite-pack-v0-2b2a00f7c4628311`.
- `../dominium`: present, branch `main`, HEAD
  `d22537869be05860d5eda70eebb2f3ed261e276c`; DCHECK queue and baseline report
  present; dirty state observed read-only.
