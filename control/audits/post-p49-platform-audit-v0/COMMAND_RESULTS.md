# Command Results

Durations are included when captured by the local command runner.

| Command | Status | Duration | Notes |
|---|---|---:|---|
| `git status --short --branch` | pass | 0.4s | `## main...origin/main` at audit start. |
| `git rev-parse HEAD` | pass | 0.4s | `4af4493c850ee431c9c7cc70e605e8cd0919a5b6`. |
| `git rev-parse origin/main` | pass | 0.4s | Same as `HEAD` at audit start. |
| `git log --oneline -n 80` | pass | 0.4s | Confirmed P49 through prior queue history. |
| `git diff --check` | pass | 0.4s | Clean. |
| `python -m unittest discover -s runtime -t .` | pass | 5.67s | 320 tests. |
| `python -m unittest discover -s surfaces -t .` | pass | 34.39s | 168 tests. |
| `python -m unittest discover -s tests -t .` | pass | 81.18s | 770 tests. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 5.62s | 53 tests. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 61.87s | 214 tests before P50 additions. |
| `python -m unittest discover -s tests/operations -t .` | pass | 3.91s | 387 tests before P50 additions. |
| `python -m unittest discover -s tests/parity -t .` | pass | 3.14s | 25 tests. |
| `python -m unittest discover -s tests/evals -t .` | pass | 3.92s | 45 tests. |
| `python scripts/check_architecture_boundaries.py` | pass | 0.49s | 445 Python files checked. |
| `python scripts/validate_repository_layout.py` | pass | 0.27s | `site/dist`, `external`, layout valid. |
| `python site/build.py --check` | pass | 1.02s | Static artifact current. |
| `python site/build.py --json` | pass | 0.92s | Status valid. |
| `python site/validate.py` | pass | 0.18s | 9 pages. |
| `python site/validate.py --json` | pass | 0.11s | Status valid. |
| `python scripts/validate_public_static_site.py` | pass | 0.10s | 9 pages, 15 source IDs checked. |
| `python scripts/validate_publication_inventory.py` | pass | 0.08s | 49 routes, 9 static pages, 12 data paths. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | 0.18s | Static artifact valid. |
| `python scripts/generate_public_data_summaries.py --check` | pass | 0.88s | 7 data files. |
| `python scripts/generate_compatibility_surfaces.py --check` | pass | 0.08s | 21 files. |
| `python scripts/generate_static_resolver_demos.py --check` | pass | 0.07s | 8 demos. |
| `python scripts/check_generated_artifact_drift.py` | pass | 7.10s | Drift guard passed. |
| `python scripts/validate_public_search_contract.py` | pass | 0.07s | 6 registered routes. |
| `python scripts/validate_public_search_contract.py --json` | pass | 0.08s | JSON valid. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | 0.06s | 5 examples. |
| `python scripts/validate_public_search_result_card_contract.py --json` | pass | 0.07s | JSON valid. |
| `python scripts/validate_public_search_safety.py` | pass | 0.06s | Local safety policy valid. |
| `python scripts/validate_public_search_safety.py --json` | pass | 0.07s | JSON valid. |
| `python scripts/validate_local_public_search_runtime.py` | pass | 0.06s | Local/prototype runtime valid. |
| `python scripts/validate_local_public_search_runtime.py --json` | pass | 0.07s | JSON valid. |
| `python scripts/public_search_smoke.py` | pass | 0.72s | Unsafe requests blocked. |
| `python scripts/public_search_smoke.py --json` | pass | 0.57s | 30 checks, 0 failed. |
| `python scripts/validate_public_search_static_handoff.py` | pass | 0.06s | Static handoff valid. |
| `python scripts/validate_public_search_rehearsal.py` | pass | 0.07s | Local rehearsal passed. |
| `python scripts/public_alpha_smoke.py` | pass | 0.62s | Public-alpha safety checks passed. |
| `python scripts/run_public_alpha_server.py --check-config` | pass | 0.25s | Production approved false. |
| `python scripts/demo_http_api.py --mode public_alpha status` | pass | 0.56s | Public-alpha status available locally. |
| `python scripts/run_archive_resolution_evals.py` | pass | 0.35s | 6 tasks, `satisfied=6`. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | 0.41s | JSON valid. |
| `python scripts/run_search_usefulness_audit.py` | pass | 0.40s | 64 queries. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | 0.41s | JSON valid. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | 0.99s | 40 files. |
| `python scripts/report_external_baseline_status.py` | pass | 0.06s | 192 pending, 0 observed. |
| `python scripts/report_external_baseline_status.py --json` | pass | 0.07s | JSON valid. |
| `python scripts/report_external_baseline_status.py --batch batch_0 --json` | pass | 0.30s | 39 pending, 0 observed. |
| `python scripts/list_external_baseline_observations.py --batch batch_0` | pass | 0.08s | Pending slots listed. |
| `python scripts/validate_external_baseline_observations.py` | pass | 0.06s | Pending observation file valid. |
| `python scripts/validate_source_pack.py --all-examples` | fail | 0.09s | CLI drift: unrecognized argument. |
| `python scripts/validate_source_pack.py --all-examples --json` | fail | 0.07s | CLI drift: unrecognized argument. |
| `python scripts/validate_evidence_pack.py --all-examples` | fail | 0.07s | CLI drift: unrecognized argument. |
| `python scripts/validate_evidence_pack.py --all-examples --json` | fail | 0.07s | CLI drift: unrecognized argument. |
| `python scripts/validate_index_pack.py --all-examples` | fail | 0.07s | CLI drift: unrecognized argument. |
| `python scripts/validate_index_pack.py --all-examples --json` | fail | 0.07s | CLI drift: unrecognized argument. |
| `python scripts/validate_contribution_pack.py --all-examples` | fail | 0.08s | CLI drift: unrecognized argument. |
| `python scripts/validate_contribution_pack.py --all-examples --json` | fail | 0.07s | CLI drift: unrecognized argument. |
| `python scripts/validate_source_pack.py` | pass | 0.08s | Supported default example passed. |
| `python scripts/validate_source_pack.py --json` | pass | 0.08s | JSON valid. |
| `python scripts/validate_evidence_pack.py` | pass | 0.08s | Supported default example passed. |
| `python scripts/validate_evidence_pack.py --json` | pass | 0.08s | JSON valid. |
| `python scripts/validate_index_pack.py` | pass | 0.07s | Supported default example passed. |
| `python scripts/validate_index_pack.py --json` | pass | 0.09s | JSON valid. |
| `python scripts/validate_contribution_pack.py` | pass | 0.08s | Supported default example passed. |
| `python scripts/validate_contribution_pack.py --json` | pass | 0.08s | JSON valid. |
| `python scripts/validate_master_index_review_queue.py --json` | pass | 0.08s | Queue example valid. |
| `python scripts/validate_pack_set.py --all-examples` | pass | 0.38s | 5/5 examples passed. |
| `python scripts/validate_pack_set.py --all-examples --json` | pass | 0.40s | JSON valid. |
| `python scripts/validate_pack_import_report.py --all-examples` | pass | 0.07s | 3/3 examples passed. |
| `python scripts/validate_pack_import_report.py --all-examples --json` | pass | 0.08s | JSON valid. |
| `python scripts/validate_only_pack_import.py --list-examples` | pass | 0.07s | Examples listed. |
| `python scripts/validate_only_pack_import.py --all-examples` | pass | 0.41s | 5/5 examples passed. |
| `python scripts/validate_only_pack_import.py --all-examples --json` | pass | 0.40s | JSON valid. |
| `python scripts/validate_pack_import_planning.py` | pass | 0.08s | Planning valid. |
| `python scripts/validate_local_quarantine_staging_model.py` | pass | 0.06s | No staging runtime. |
| `python scripts/validate_staging_report_path_contract.py` | pass | 0.07s | Stdout default and forbidden roots valid. |
| `python scripts/validate_local_staging_manifest.py --all-examples` | pass | 0.07s | 1/1 examples passed. |
| `python scripts/validate_local_staging_manifest.py --all-examples --json` | pass | 0.07s | JSON valid. |
| `python scripts/inspect_staged_pack.py --list-examples` | pass | 0.06s | Examples listed. |
| `python scripts/inspect_staged_pack.py --all-examples` | pass | 0.07s | Read-only inspection passed. |
| `python scripts/inspect_staged_pack.py --all-examples --json` | pass | 0.07s | JSON valid. |
| `python scripts/validate_staged_pack_inspector.py` | pass | 0.13s | Inspector validator passed. |
| `python scripts/validate_ai_provider_contract.py` | pass | 0.08s | Runtime implemented false. |
| `python scripts/validate_ai_provider_contract.py --json` | pass | 0.09s | JSON valid. |
| `python scripts/validate_ai_provider_contract.py --strict` | pass | 0.08s | Strict passed. |
| `python scripts/validate_ai_output.py --all-examples` | pass | 0.07s | 4/4 examples passed. |
| `python scripts/validate_ai_output.py --all-examples --json` | pass | 0.07s | JSON valid. |
| `python scripts/validate_ai_assisted_drafting_plan.py` | pass | 0.08s | No model calls. |
| `python scripts/validate_ai_assisted_drafting_plan.py --json` | pass | 0.07s | JSON valid. |
| `python -m unittest discover -s runtime/engine/ai -t .` | pass | 0.10s | 8 tests. |
| `python scripts/validate_live_backend_handoff.py` | pass | 0.11s | Contract valid. |
| `python scripts/validate_live_probe_gateway.py` | pass | 0.25s | 9 disabled candidate sources. |
| `python scripts/generate_static_snapshot.py --check` | pass | 0.07s | 12 files. |
| `python scripts/validate_static_snapshot.py` | pass | 0.09s | 11 checksum entries. |
| `python scripts/validate_snapshot_consumer_contract.py` | pass | 0.16s | No consumer runtime. |
| `python scripts/validate_native_client_contract.py` | pass | 0.12s | CLI true, native GUI false. |
| `python scripts/validate_action_policy.py` | pass | 0.07s | Current risky actions disabled. |
| `python scripts/validate_local_cache_privacy_policy.py` | pass | 0.06s | No telemetry/accounts/cloud sync. |
| `python scripts/validate_relay_surface_design.py` | pass | 0.24s | No relay services. |
| `python scripts/validate_relay_prototype_plan.py` | pass | 0.11s | Approval required. |
| `python scripts/validate_windows_winforms_skeleton_plan.py` | pass | 0.13s | Approval required. |
| `python scripts/validate_native_project_readiness_review.py` | pass | 0.14s | Ready after human approval. |
| `python scripts/check_rust_source_registry_parity.py` | pass | 0.07s | Structure passed; Cargo unavailable. |
| `python scripts/check_rust_query_planner_parity.py` | pass | 0.08s | Structure passed; Cargo unavailable. |
| `python scripts/validate_rust_local_index_parity_plan.py` | pass | 0.16s | Plan passed. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | 0.30s | 28 required files checked. |
| `python scripts/validate_post_p49_platform_audit.py --json` | pass | 0.30s | JSON parsed with no errors. |
| `python -m unittest tests.operations.test_post_p49_platform_audit tests.scripts.test_validate_post_p49_platform_audit` | pass | 0.50s | 7 focused P50 tests passed. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 59.11s | Final run: 216 tests. |
| `python -m unittest discover -s tests/operations -t .` | pass | 3.91s | Final run: 392 tests. |
| `python -m unittest discover -s tests/hardening -t .` | fail | 5.49s | First final run found hardening allow-list drift for the new audit validator. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 5.90s | Rerun after metadata repair: 53 tests. |
| `python -m unittest discover -s runtime -t .` | pass | 4.76s | Final run: 320 tests. |
| `python -m unittest discover -s surfaces -t .` | pass | 31.05s | Final run: 168 tests. |
| `python -m unittest discover -s tests -t .` | fail | 76.80s | First final run failed only because of the hardening allow-list drift. |
| `python -m unittest discover -s tests -t .` | pass | 77.30s | Rerun after metadata repair: 777 tests. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | n/a | Cargo unavailable in PATH. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | n/a | Cargo unavailable in PATH. |

Read-only inspection commands also included `rg --files`, targeted `rg -n`,
`Get-ChildItem`, `Get-Content`, `Test-Path`, and JSON parsing commands. They
did not edit files, call networks, or run live probes.
