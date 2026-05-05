# Command Results

Initial inspection:

- `git status --short --branch`: `## main...origin/main`
- `git rev-parse HEAD`: `0edf1fcfba7fc90513aaefee3363cbf3598b6ffa`
- `git rev-parse origin/main`: `0edf1fcfba7fc90513aaefee3363cbf3598b6ffa`
- `git log --oneline -n 80`: P97/P96/P95/P94/P93 and earlier audit/contract history present.

Pre-audit checks:

- `python scripts/run_source_cache_dry_run.py --all-examples --json`: passed, 5 candidates seen, 5 valid, 0 invalid.
- `python scripts/validate_source_cache_record.py --all-examples --json`: passed, 3 canonical P70 examples valid.
- `python scripts/validate_source_cache_contract.py --json`: passed.

Final verification:

- `python scripts/run_source_cache_dry_run.py --all-examples --json`: passed, 5 candidates seen, 5 valid, 0 invalid.
- `python scripts/validate_source_cache_dry_run_report.py`: passed.
- `python scripts/validate_source_cache_dry_run_report.py --json`: passed.
- P97/P96/P95/P94/P93 planning/contract validators: passed.
- Connector runtime planning validators P87-P92: passed.
- Public query observation, identity, merge, ranking, page, source-cache, and evidence-ledger validators: passed.
- External baseline comparison runner/report validator: passed; comparison remains not eligible because Batch 0 has 0 observed and 39 pending manual slots.
- Hosted deployment verifier/evidence validator: verifier ran; static URL still returns 404 for required routes and backend URL is not configured; evidence validator passed with hosted deployment unverified/operator-gated.
- Public search contract, result card, safety, local runtime, smoke, safety evidence, hosted rehearsal: passed.
- Static site build/check, publication inventory, static site validation, generated artifact drift guard: passed.
- Archive resolution evals: passed, `satisfied=6`.
- Search usefulness audit: passed, status counts `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`.
- External baseline status: valid, all 192 global slots pending manual observation.
- Python oracle golden check: passed.
- `python -m unittest discover -s tests/scripts -t .`: passed, 644 tests.
- `python -m unittest discover -s tests/operations -t .`: passed, 604 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed, 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed, 25 tests.
- `python -m unittest discover -s runtime -t .`: passed, 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed, 168 tests.
- `python -m unittest discover -s tests/runtime -t .`: passed, 6 tests.
- `python -m unittest discover -s tests -t .`: passed, 1423 tests.
- `python scripts/check_architecture_boundaries.py`: passed, 452 files checked, no violations.
- `git diff --check`: passed with line-ending warnings only.
- `cargo --version`: unavailable; Cargo is not installed, so optional Cargo checks were not run.
