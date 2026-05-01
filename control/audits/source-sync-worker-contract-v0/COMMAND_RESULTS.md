# Command Results

P69 verification results are sanitized: command output tails are omitted to avoid committing local paths or private machine details.

| Command | Status | Return code | Duration (s) |
| --- | --- | ---: | ---: |
| `python scripts/validate_source_sync_worker_job.py --all-examples` | passed | 0 | 0.078 |
| `python scripts/validate_source_sync_worker_job.py --all-examples --json` | passed | 0 | 0.062 |
| `python scripts/validate_source_sync_worker_contract.py` | passed | 0 | 0.078 |
| `python scripts/validate_source_sync_worker_contract.py --json` | passed | 0 | 0.079 |
| `python scripts/dry_run_source_sync_worker_job.py --label "IA metadata sync example" --kind internet_archive_metadata_sync --source-family internet_archive --json` | passed | 0 | 0.046 |
| `python scripts/validate_demand_dashboard_snapshot.py --all-examples` | passed | 0 | 0.063 |
| `python scripts/validate_demand_dashboard_contract.py` | passed | 0 | 0.078 |
| `python scripts/validate_query_guard_decision.py --all-examples` | passed | 0 | 0.047 |
| `python scripts/validate_query_privacy_poisoning_guard_contract.py` | passed | 0 | 0.078 |
| `python scripts/validate_known_absence_page.py --all-examples` | passed | 0 | 0.047 |
| `python scripts/validate_known_absence_page_contract.py` | passed | 0 | 0.062 |
| `python scripts/validate_candidate_promotion_assessment.py --all-examples` | passed | 0 | 0.063 |
| `python scripts/validate_candidate_promotion_policy.py` | passed | 0 | 0.062 |
| `python scripts/validate_candidate_index_record.py --all-examples` | passed | 0 | 0.063 |
| `python scripts/validate_candidate_index_contract.py` | passed | 0 | 0.062 |
| `python scripts/validate_probe_queue_item.py --all-examples` | passed | 0 | 0.047 |
| `python scripts/validate_probe_queue_contract.py` | passed | 0 | 0.063 |
| `python scripts/validate_search_need_record.py --all-examples` | passed | 0 | 0.062 |
| `python scripts/validate_search_need_record_contract.py` | passed | 0 | 0.063 |
| `python scripts/validate_search_miss_ledger_entry.py --all-examples` | passed | 0 | 0.047 |
| `python scripts/validate_search_miss_ledger_contract.py` | passed | 0 | 0.062 |
| `python scripts/validate_search_result_cache_entry.py --all-examples` | passed | 0 | 0.063 |
| `python scripts/validate_shared_query_result_cache_contract.py` | passed | 0 | 0.047 |
| `python scripts/validate_query_observation.py --all-examples` | passed | 0 | 0.062 |
| `python scripts/validate_query_observation_contract.py` | passed | 0 | 0.063 |
| `python scripts/validate_live_probe_gateway.py` | passed | 0 | 0.218 |
| `python scripts/run_hosted_public_search_rehearsal.py` | passed | 0 | 1.016 |
| `python scripts/validate_hosted_public_search_rehearsal.py` | passed | 0 | 1.000 |
| `python scripts/run_public_search_safety_evidence.py` | passed | 0 | 0.406 |
| `python scripts/validate_public_search_safety_evidence.py` | passed | 0 | 0.391 |
| `python scripts/validate_static_site_search_integration.py` | passed | 0 | 0.062 |
| `python scripts/validate_public_search_index_builder.py` | passed | 0 | 0.828 |
| `python scripts/validate_public_search_index.py` | passed | 0 | 0.250 |
| `python scripts/validate_hosted_public_search_wrapper.py` | passed | 0 | 0.266 |
| `python scripts/check_hosted_public_search_wrapper.py` | passed | 0 | 0.250 |
| `python scripts/run_hosted_public_search.py --check-config` | passed | 0 | 0.219 |
| `python scripts/validate_public_search_production_contract.py` | passed | 0 | 0.047 |
| `python scripts/validate_static_deployment_evidence.py` | passed | 0 | 0.062 |
| `python scripts/validate_post_p50_remediation.py` | passed | 0 | 0.047 |
| `python scripts/validate_post_p49_platform_audit.py` | passed | 0 | 0.047 |
| `python scripts/validate_public_search_contract.py` | passed | 0 | 0.062 |
| `python scripts/validate_public_search_result_card_contract.py` | passed | 0 | 0.047 |
| `python scripts/validate_public_search_safety.py` | passed | 0 | 0.047 |
| `python scripts/validate_local_public_search_runtime.py` | passed | 0 | 0.063 |
| `python scripts/public_search_smoke.py` | passed | 0 | 0.531 |
| `python scripts/public_search_smoke.py --json` | passed | 0 | 0.531 |
| `python scripts/build_public_search_index.py --check` | passed | 0 | 0.469 |
| `python site/build.py --check` | passed | 0 | 0.984 |
| `python site/validate.py` | passed | 0 | 0.094 |
| `python scripts/validate_publication_inventory.py` | passed | 0 | 0.063 |
| `python scripts/validate_public_static_site.py` | passed | 0 | 0.078 |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | passed | 0 | 0.140 |
| `python scripts/check_generated_artifact_drift.py` | passed | 0 | 9.407 |
| `python scripts/public_alpha_smoke.py` | passed | 0 | 0.578 |
| `python scripts/run_archive_resolution_evals.py` | passed | 0 | 0.312 |
| `python scripts/run_archive_resolution_evals.py --json` | passed | 0 | 0.313 |
| `python scripts/run_search_usefulness_audit.py` | passed | 0 | 0.343 |
| `python scripts/run_search_usefulness_audit.py --json` | passed | 0 | 0.375 |
| `python scripts/report_external_baseline_status.py --json` | passed | 0 | 0.047 |
| `python scripts/generate_python_oracle_golden.py --check` | passed | 0 | 0.875 |
| `python -m unittest discover -s tests/scripts -t .` | passed | 0 | 91.563 |
| `python -m unittest discover -s tests/operations -t .` | passed | 0 | 8.719 |
| `python -m unittest discover -s tests/hardening -t .` | passed | 0 | 5.468 |
| `python -m unittest discover -s tests/parity -t .` | passed | 0 | 1.500 |
| `python -m unittest discover -s runtime -t .` | passed | 0 | 4.969 |
| `python -m unittest discover -s surfaces -t .` | passed | 0 | 30.797 |
| `python -m unittest discover -s tests -t .` | passed | 0 | 114.062 |
| `python scripts/check_architecture_boundaries.py` | passed | 0 | 0.485 |
| `git diff --check` | passed | 0 | 0.094 |
| `git status --short --branch` | passed | 0 | 0.046 |
| `cargo --version` | skipped_unavailable |  | 0.000 |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | skipped_unavailable |  | 0.000 |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | skipped_unavailable |  | 0.000 |
