# Command Results

Initial inspection:

- `git status --short --branch`: clean at start.
- `git rev-parse HEAD`: `ed3ced416825fa7af520f7370f97d09bf86121d0`.
- `git rev-parse origin/main`: `ed3ced416825fa7af520f7370f97d09bf86121d0`.
- `git log --oneline -n 100`: P104 through P95 and earlier contract/runtime
  planning packs present in recent history.

Final verification results are recorded in the JSON report after the P105
validator and tests run.

P105 commands:

- `python scripts/validate_deep_extraction_runtime_plan.py`: passed.
- `python scripts/validate_deep_extraction_runtime_plan.py --json`: passed.

Adjacent dry-run and planning validators:

- `python scripts/run_pack_import_dry_run.py --all-examples --json`: passed.
- `python scripts/validate_pack_import_dry_run_report.py`: passed.
- `python scripts/run_page_dry_run.py --all-examples --json`: passed.
- `python scripts/validate_page_dry_run_report.py`: passed.
- `python scripts/validate_manual_observation_batch_0_follow_up.py`: passed;
  Batch 0 remains pending with 0 observed and 39 pending records.
- `python scripts/validate_connector_approval_runtime_planning_audit.py`: passed.
- `python scripts/validate_public_search_runtime_integration_audit.py`: passed.
- `python scripts/run_evidence_ledger_dry_run.py --all-examples --json`: passed.
- `python scripts/validate_evidence_ledger_dry_run_report.py`: passed.
- `python scripts/run_source_cache_dry_run.py --all-examples --json`: passed.
- `python scripts/validate_source_cache_dry_run_report.py`: passed.
- `python scripts/validate_public_search_ranking_runtime_plan.py`: passed.
- `python scripts/validate_search_result_explanation_contract.py`: passed.
- `python scripts/validate_deep_extraction_contract.py`: passed.
- `python scripts/validate_pack_import_runtime_plan.py`: passed.
- `python scripts/validate_page_runtime_plan.py`: passed.
- `python scripts/validate_deep_extraction_request.py --all-examples`: passed,
  7 examples.
- `python scripts/validate_extraction_result_summary.py --all-examples`: passed,
  7 examples.

Public search, baseline, and eval checks:

- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`: passed;
  comparison remains not eligible because no manual observations are present.
- `python scripts/validate_external_baseline_comparison_report.py`: passed.
- `python scripts/validate_public_search_contract.py`: passed.
- `python scripts/validate_public_search_result_card_contract.py`: passed.
- `python scripts/validate_public_search_safety.py`: passed.
- `python scripts/validate_local_public_search_runtime.py`: passed.
- `python scripts/public_search_smoke.py`: passed.
- `python scripts/public_search_smoke.py --json`: passed.
- `python scripts/run_archive_resolution_evals.py`: passed; 6 local tasks
  satisfied.
- `python scripts/run_archive_resolution_evals.py --json`: passed.
- `python scripts/run_search_usefulness_audit.py`: passed; local usefulness
  observations remain partial.
- `python scripts/run_search_usefulness_audit.py --json`: passed.

Unit and architecture checks:

- `python -m unittest discover -s tests/runtime -t .`: passed, 27 tests.
- `python -m unittest discover -s tests/scripts -t .`: passed, 698 tests.
- `python -m unittest discover -s tests/operations -t .`: passed, 636 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed, 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed, 25 tests.
- `python -m unittest discover -s runtime -t .`: passed, 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed, 168 tests.
- `python -m unittest discover -s tests -t .`: passed, 1530 tests.
- `python scripts/check_architecture_boundaries.py`: passed.
- `git diff --check`: passed; Git emitted CRLF normalization warnings for
  existing `site/dist` files.

Optional local command availability:

- `gh`: not available in PATH; GitHub Actions status was not checked.
- `cargo`: not available in PATH; optional cargo checks were not run.
