# Command Results

- Passed: 68
- Failed: 0
- Skipped: 3
- Output policy: command output tails are omitted from the JSON report to avoid local path or private machine detail retention.

| Status | Command | Notes |
| --- | --- | --- |
| passed | `python scripts/validate_demand_dashboard_snapshot.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_demand_dashboard_snapshot.py --all-examples --json` | completed without recording command output |
| passed | `python scripts/validate_demand_dashboard_contract.py` | completed without recording command output |
| passed | `python scripts/validate_demand_dashboard_contract.py --json` | completed without recording command output |
| passed | `python scripts/dry_run_demand_dashboard_snapshot.py --json` | completed without recording command output |
| passed | `python scripts/validate_query_guard_decision.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_query_privacy_poisoning_guard_contract.py` | completed without recording command output |
| passed | `python scripts/validate_known_absence_page.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_known_absence_page_contract.py` | completed without recording command output |
| passed | `python scripts/validate_candidate_promotion_assessment.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_candidate_promotion_policy.py` | completed without recording command output |
| passed | `python scripts/validate_candidate_index_record.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_candidate_index_contract.py` | completed without recording command output |
| passed | `python scripts/validate_probe_queue_item.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_probe_queue_contract.py` | completed without recording command output |
| passed | `python scripts/validate_search_need_record.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_search_need_record_contract.py` | completed without recording command output |
| passed | `python scripts/validate_search_miss_ledger_entry.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_search_miss_ledger_contract.py` | completed without recording command output |
| passed | `python scripts/validate_search_result_cache_entry.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_shared_query_result_cache_contract.py` | completed without recording command output |
| passed | `python scripts/validate_query_observation.py --all-examples` | completed without recording command output |
| passed | `python scripts/validate_query_observation_contract.py` | completed without recording command output |
| passed | `python scripts/run_hosted_public_search_rehearsal.py` | completed without recording command output |
| passed | `python scripts/validate_hosted_public_search_rehearsal.py` | completed without recording command output |
| passed | `python scripts/run_public_search_safety_evidence.py` | completed without recording command output |
| passed | `python scripts/validate_public_search_safety_evidence.py` | completed without recording command output |
| passed | `python scripts/validate_static_site_search_integration.py` | completed without recording command output |
| passed | `python scripts/validate_public_search_index_builder.py` | completed without recording command output |
| passed | `python scripts/validate_public_search_index.py` | completed without recording command output |
| passed | `python scripts/validate_hosted_public_search_wrapper.py` | completed without recording command output |
| passed | `python scripts/check_hosted_public_search_wrapper.py` | completed without recording command output |
| passed | `python scripts/run_hosted_public_search.py --check-config` | completed without recording command output |
| passed | `python scripts/validate_public_search_production_contract.py` | completed without recording command output |
| passed | `python scripts/validate_static_deployment_evidence.py` | completed without recording command output |
| passed | `python scripts/validate_post_p50_remediation.py` | completed without recording command output |
| passed | `python scripts/validate_post_p49_platform_audit.py` | completed without recording command output |
| passed | `python scripts/validate_live_probe_gateway.py` | completed without recording command output |
| passed | `python scripts/validate_public_search_contract.py` | completed without recording command output |
| passed | `python scripts/validate_public_search_result_card_contract.py` | completed without recording command output |
| passed | `python scripts/validate_public_search_safety.py` | completed without recording command output |
| passed | `python scripts/validate_local_public_search_runtime.py` | completed without recording command output |
| passed | `python scripts/public_search_smoke.py` | completed without recording command output |
| passed | `python scripts/public_search_smoke.py --json` | completed without recording command output |
| passed | `python scripts/build_public_search_index.py --check` | completed without recording command output |
| passed | `python site/build.py --check` | completed without recording command output |
| passed | `python site/validate.py` | completed without recording command output |
| passed | `python scripts/validate_publication_inventory.py` | completed without recording command output |
| passed | `python scripts/validate_public_static_site.py` | completed without recording command output |
| passed | `python scripts/check_github_pages_static_artifact.py --path site/dist` | completed without recording command output |
| passed | `python scripts/check_generated_artifact_drift.py` | completed without recording command output |
| passed | `python scripts/public_alpha_smoke.py` | completed without recording command output |
| passed | `python scripts/run_archive_resolution_evals.py` | completed without recording command output |
| passed | `python scripts/run_archive_resolution_evals.py --json` | completed without recording command output |
| passed | `python scripts/run_search_usefulness_audit.py` | completed without recording command output |
| passed | `python scripts/run_search_usefulness_audit.py --json` | completed without recording command output |
| passed | `python scripts/report_external_baseline_status.py --json` | completed without recording command output |
| passed | `python scripts/generate_python_oracle_golden.py --check` | completed without recording command output |
| passed | `python -m unittest discover -s tests/scripts -t .` | completed without recording command output |
| passed | `python -m unittest discover -s tests/operations -t .` | completed without recording command output |
| passed | `python -m unittest discover -s tests/hardening -t .` | completed without recording command output |
| passed | `python -m unittest discover -s tests/parity -t .` | completed without recording command output |
| passed | `python -m unittest discover -s runtime -t .` | completed without recording command output |
| passed | `python -m unittest discover -s surfaces -t .` | completed without recording command output |
| passed | `python -m unittest discover -s tests -t .` | completed without recording command output |
| passed | `python scripts/check_architecture_boundaries.py` | completed without recording command output |
| passed | `git diff --check` | completed without recording command output |
| passed | `git status --short --branch` | completed without recording command output |
| skipped | `cargo --version` | optional tool cargo is unavailable |
| skipped | `cargo check --workspace --manifest-path crates/Cargo.toml` | optional tool cargo is unavailable |
| skipped | `cargo test --workspace --manifest-path crates/Cargo.toml` | optional tool cargo is unavailable |
