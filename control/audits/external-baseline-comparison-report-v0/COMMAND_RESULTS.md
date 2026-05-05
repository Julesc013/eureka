# Command Results

Final P78 verification completed successfully.

- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`: passed; `eligibility=no_observations`, observed=0, pending=39, compared=0.
- `python scripts/validate_external_baseline_comparison_report.py`: passed with the expected no-observations warning.
- `python scripts/validate_external_baseline_comparison_report.py --json`: passed and parsed.
- `python scripts/report_external_baseline_status.py --json`: passed; global observed=0, pending=192.
- `python scripts/list_external_baseline_observations.py --batch batch_0`: passed; Batch 0 has 39 pending slots.
- `python scripts/validate_external_baseline_observations.py`: passed.
- `python scripts/run_search_usefulness_audit.py` and `--json`: passed; covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2.
- `python scripts/run_archive_resolution_evals.py` and `--json`: passed; 6/6 satisfied.
- P77 hosted deployment verifier/validator: passed, while preserving static failed/backend not configured evidence.
- P71-P76 connector approval validators: passed.
- P59-P70 query/source contract validators: passed.
- Public search/static/publication validators and smokes: passed.
- Unit discovery lanes for tests/scripts, tests/operations, tests/hardening, tests/parity, runtime, surfaces, and tests: passed.
- `python scripts/check_architecture_boundaries.py`: passed.
- `git diff --check`: passed with CRLF warnings only for existing generated static files.
- `gh --version`: unavailable; GitHub Actions status unverified.
- `cargo --version`: unavailable; Cargo checks not run.
