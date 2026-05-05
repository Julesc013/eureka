# Command Results

Initial inspection:

- `git status --short --branch`: `## main...origin/main`
- `git rev-parse HEAD`: `f279e097476cd8df31e31dea6504a481a9650c44`
- `git rev-parse origin/main`: `f279e097476cd8df31e31dea6504a481a9650c44`
- `git log --oneline -n 100`: inspected locally.

P106 verification results are recorded in
`search_result_explanation_runtime_planning_report.json` after validation.

Verification performed:

- `python scripts/validate_search_result_explanation_runtime_plan.py`: passed
- `python scripts/validate_search_result_explanation_runtime_plan.py --json`: passed
- Adjacent P100-P105/P96/P97/contract validators requested for P106: passed
- External baseline comparison report commands: passed; no external observation
  was performed by P106
- Public search contract/card/safety/local runtime/smoke commands: passed
- Archive resolution evals and search usefulness audit commands: passed
- `python -m unittest discover -s tests/runtime -t .`: 27 passed
- `python -m unittest discover -s tests/scripts -t .`: 712 passed
- `python -m unittest discover -s tests/operations -t .`: 643 passed
- `python -m unittest discover -s tests/hardening -t .`: 53 passed
- `python -m unittest discover -s tests/parity -t .`: 25 passed
- `python -m unittest discover -s runtime -t .`: 320 passed
- `python -m unittest discover -s surfaces -t .`: 168 passed
- `python -m unittest discover -s tests -t .`: 1551 passed
- `python scripts/check_architecture_boundaries.py`: passed, 472 Python files
  checked
- `git diff --check`: passed with existing CRLF normalization warnings for
  `site/dist` files
- `gh --version`: unavailable on PATH; GitHub Actions status unverified
- `cargo --version`: unavailable on PATH; Cargo checks not run
