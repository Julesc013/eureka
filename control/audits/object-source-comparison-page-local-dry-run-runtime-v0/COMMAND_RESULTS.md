# Command Results

Initial implementation commands:

- `git status --short --branch`: clean at start.
- `git rev-parse HEAD`: `1148f87b9dea06d69293272a175c9cf6f51c1c34`.
- `git rev-parse origin/main`: `1148f87b9dea06d69293272a175c9cf6f51c1c34`.
- `git log --oneline -n 100`: P102, P101, P100, P99, P98, P97, P96, P95, P94, P93, P81, P80, and P79 packs present in recent history.
- `python scripts/run_page_dry_run.py --all-examples --json`: passed; 18 pages seen, 18 valid, 0 invalid.
- `python scripts/run_page_dry_run.py --all-examples --render-preview --json`: passed; 18 preview outputs generated in JSON.

Final verification:

- `python scripts/run_page_dry_run.py --all-examples --json`: passed; 18 pages seen, 18 valid, 0 invalid.
- `python scripts/run_page_dry_run.py --all-examples --render-preview --json`: passed; 18 preview outputs generated in JSON.
- `python scripts/validate_page_dry_run_report.py`: passed.
- `python scripts/validate_page_dry_run_report.py --json`: passed.
- `python scripts/validate_manual_observation_batch_0_follow_up.py`: passed; Batch 0 remains pending with 39 pending observations and 0 observed.
- `python scripts/validate_connector_approval_runtime_planning_audit.py`: passed.
- `python scripts/validate_public_search_runtime_integration_audit.py`: passed.
- `python scripts/run_evidence_ledger_dry_run.py --all-examples --json`: passed; 7 candidates valid.
- `python scripts/validate_evidence_ledger_dry_run_report.py`: passed.
- `python scripts/run_source_cache_dry_run.py --all-examples --json`: passed; 5 candidates valid.
- `python scripts/validate_source_cache_dry_run_report.py`: passed.
- `python scripts/validate_public_search_ranking_runtime_plan.py`: passed.
- `python scripts/validate_search_result_explanation_contract.py`: passed.
- `python scripts/validate_deep_extraction_contract.py`: passed.
- `python scripts/validate_pack_import_runtime_plan.py`: passed.
- `python scripts/validate_page_runtime_plan.py`: passed.
- `python scripts/validate_object_page_contract.py`: passed; 4 examples, contract-only warning retained.
- `python scripts/validate_source_page_contract.py`: passed; 4 examples, contract-only warning retained.
- `python scripts/validate_comparison_page_contract.py`: passed; 5 examples.
- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`: passed; comparison not eligible because 0 observations are complete and 39 are pending.
- `python scripts/validate_external_baseline_comparison_report.py`: passed with manual-baseline warning.
- `python scripts/validate_public_hosted_deployment_evidence.py`: passed; hosted backend remains not configured/unverified.
- `python scripts/verify_public_hosted_deployment.py --from-repo-config --json`: skipped because P103 prohibits deployed hosted/web verification and external calls.
- `python scripts/validate_public_search_contract.py`: passed.
- `python scripts/validate_public_search_result_card_contract.py`: passed.
- `python scripts/validate_public_search_safety.py`: passed.
- `python scripts/validate_local_public_search_runtime.py`: passed.
- `python scripts/public_search_smoke.py`: passed; 30/30 checks.
- `python scripts/public_search_smoke.py --json`: passed; 30/30 checks.
- `python scripts/run_public_search_safety_evidence.py`: passed; 64/64 checks.
- `python scripts/validate_public_search_safety_evidence.py`: passed.
- `python scripts/run_hosted_public_search_rehearsal.py`: passed; localhost-only rehearsal, 60/60 checks.
- `python scripts/validate_hosted_public_search_rehearsal.py`: passed; hosted deployment remains operator-gated/unverified.
- `python site/build.py --check`: passed.
- `python site/validate.py`: passed.
- `python scripts/validate_publication_inventory.py`: passed.
- `python scripts/validate_public_static_site.py`: passed.
- `python scripts/check_github_pages_static_artifact.py --path site/dist`: passed.
- `python scripts/check_generated_artifact_drift.py`: passed.
- `python scripts/run_archive_resolution_evals.py`: passed; 6/6 tasks satisfied.
- `python scripts/run_archive_resolution_evals.py --json`: passed; 6/6 tasks satisfied.
- `python scripts/run_search_usefulness_audit.py`: passed; 64 queries, status counts capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2.
- `python scripts/run_search_usefulness_audit.py --json`: passed with the same status counts.
- `python scripts/report_external_baseline_status.py --json`: passed; manual external observations remain pending.
- `python scripts/generate_python_oracle_golden.py --check`: passed.
- `python -m unittest discover -s tests/runtime -t .`: passed; 23 tests.
- `python -m unittest discover -s tests/scripts -t .`: passed; 676 tests.
- `python -m unittest discover -s tests/operations -t .`: passed; 626 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed; 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed; 25 tests.
- `python -m unittest discover -s runtime -t .`: passed; 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed; 168 tests.
- `python -m unittest discover -s tests -t .`: passed; 1494 tests.
- `python scripts/check_architecture_boundaries.py`: passed; no boundary violations.
- `git diff --check`: passed with line-ending warnings only.
- `gh --version`: unavailable; GitHub Actions status not checked.
- `cargo --version`: unavailable; optional Cargo checks not run.
