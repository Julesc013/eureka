# Command Results

Initial inspection commands:

| Command | Result |
|---|---|
| `git status --short --branch` | Clean at inspection: `## main...origin/main`. |
| `git rev-parse HEAD` | `7e0538265736e765bddcf7bda3048807f573fffe`. |
| `git rev-parse origin/main` | `7e0538265736e765bddcf7bda3048807f573fffe`. |
| `git log --oneline -n 100` | Confirmed P101 was the latest completed milestone before P102. |
| `python scripts/report_external_baseline_status.py --json` | Ready; Batch 0 pending 39, observed 0; global pending 192, observed 0. |
| `python scripts/list_external_baseline_observations.py --batch batch_0 --json` | Ready; 39 slots listed, all pending. |
| `python scripts/validate_external_baseline_observations.py --json` | Valid; no errors; Batch 0 pending 39, observed 0. |
| `python scripts/run_external_baseline_comparison.py --batch batch_0 --json` | Ok true; eligibility `no_observations`; compared count 0. |

Final verification commands:

| Command | Result |
|---|---|
| `python scripts/validate_manual_observation_batch_0_follow_up.py` | Passed. |
| `python scripts/validate_manual_observation_batch_0_follow_up.py --json` | Passed and emitted parseable JSON. |
| `python scripts/report_manual_observation_batch_0_status.py --json` | Passed; Batch 0 pending 39, observed 0. |
| `python scripts/report_external_baseline_status.py --json` | Passed; global baseline pending 192, observed 0. |
| `python scripts/list_external_baseline_observations.py --batch batch_0` | Passed; listed 39 pending slots. |
| `python scripts/validate_external_baseline_observations.py` | Passed; observation pack valid. |
| `python scripts/run_external_baseline_comparison.py --batch batch_0 --json` | Passed; eligibility `no_observations`, compared 0. |
| `python scripts/validate_external_baseline_comparison_report.py` | Passed with expected warning that no manual observations are present. |
| `python scripts/validate_connector_approval_runtime_planning_audit.py` | Passed. |
| `python scripts/validate_public_search_runtime_integration_audit.py` | Passed. |
| `python scripts/run_evidence_ledger_dry_run.py --all-examples --json` | Passed; 7 synthetic examples valid. |
| `python scripts/validate_evidence_ledger_dry_run_report.py` | Passed. |
| `python scripts/run_source_cache_dry_run.py --all-examples --json` | Passed; 5 synthetic examples valid. |
| `python scripts/validate_source_cache_dry_run_report.py` | Passed. |
| `python scripts/validate_public_search_ranking_runtime_plan.py` | Passed. |
| `python scripts/validate_search_result_explanation_contract.py` | Passed; 53 items checked. |
| `python scripts/validate_deep_extraction_contract.py` | Passed; 49 items checked. |
| `python scripts/validate_pack_import_runtime_plan.py` | Passed. |
| `python scripts/validate_page_runtime_plan.py` | Passed. |
| `python scripts/validate_public_search_contract.py` | Passed. |
| `python scripts/validate_public_search_result_card_contract.py` | Passed. |
| `python scripts/validate_public_search_safety.py` | Passed. |
| `python scripts/validate_local_public_search_runtime.py` | Passed. |
| `python scripts/public_search_smoke.py` | Passed; 30/30 checks. |
| `python scripts/public_search_smoke.py --json` | Passed. |
| `python scripts/run_archive_resolution_evals.py` | Passed; 6 tasks satisfied. |
| `python scripts/run_archive_resolution_evals.py --json` | Passed. |
| `python scripts/run_search_usefulness_audit.py` | Passed; covered 5, partial 40, source_gap 10, capability_gap 7, unknown 2. |
| `python scripts/run_search_usefulness_audit.py --json` | Passed. |
| `python -m unittest discover -s tests/runtime -t .` | Passed; 14 tests. |
| `python -m unittest discover -s tests/scripts -t .` | Passed; 667 tests. |
| `python -m unittest discover -s tests/operations -t .` | Passed; 623 tests. |
| `python -m unittest discover -s tests/hardening -t .` | Passed; 53 tests. |
| `python -m unittest discover -s tests/parity -t .` | Passed; 25 tests. |
| `python -m unittest discover -s runtime -t .` | Passed; 320 tests. |
| `python -m unittest discover -s surfaces -t .` | Passed; 168 tests. |
| `python -m unittest discover -s tests -t .` | Passed; 1473 tests. |
| `python scripts/check_architecture_boundaries.py` | Passed; no violations. |
| `git diff --check` | Passed with LF-to-CRLF working-copy warnings. |
| `git status --short --branch` | Showed P102 files pending commit. |

Optional `gh` and `cargo` commands were not run for P102; they are not required for this local planning/validator milestone and `gh auth status` could touch external service context.
