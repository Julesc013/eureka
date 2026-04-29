# Command Results

Status vocabulary:

- `passed`: command exited successfully.
- `unavailable`: command could not run because the required tool is not available locally.

| Command | Status | Summary |
| --- | --- | --- |
| `git status --short --branch` | passed | `## main...origin/main` |
| `git log --oneline -n 20` | passed | Latest commit at capture: `57e8fa6 chore(relay): publish prototype planning metadata` |
| `git diff --check` | passed | No whitespace errors. |
| `python scripts/validate_full_project_state_audit.py` | passed | 23 required audit files checked. |
| `python scripts/validate_full_project_state_audit.py --json` | passed | JSON validator output parsed with no errors. |
| `python -m unittest tests.operations.test_full_project_state_audit tests.scripts.test_validate_full_project_state_audit` | passed | 6 focused audit tests passed. |
| `python -m unittest discover -s tests/scripts -t .` | passed | 94 tests passed. |
| `python -m unittest discover -s tests/operations -t .` | passed | 218 tests passed. |
| `python -m unittest discover -s tests/hardening -t .` | passed | 46 tests passed. |
| `python -m unittest discover -s tests/parity -t .` | passed | 25 tests passed. |
| `python -m unittest discover -s tests/evals -t .` | passed | 43 tests passed. |
| `python -m unittest discover -s runtime -t .` | passed | 299 tests passed. |
| `python -m unittest discover -s surfaces -t .` | passed | 162 tests passed. |
| `python -m unittest discover -s tests -t .` | passed | 471 tests passed. |
| `python scripts/check_architecture_boundaries.py` | passed | 428 Python files checked; no boundary violations. |
| `python scripts/generate_python_oracle_golden.py --check` | passed | Python oracle golden pack valid; 40 files. |
| `python scripts/run_archive_resolution_evals.py` | passed | 6 archive tasks; satisfied=6. |
| `python scripts/run_archive_resolution_evals.py --json` | passed | JSON report emitted. |
| `python scripts/run_search_usefulness_audit.py` | passed | 64 queries; covered=5, partial=22, source_gap=26, capability_gap=9, unknown=2. |
| `python scripts/run_search_usefulness_audit.py --json` | passed | JSON report emitted. |
| `python scripts/validate_publication_inventory.py` | passed | 43 registered routes; 8 pages; 9 client profiles; 10 public data paths. |
| `python scripts/validate_publication_inventory.py --json` | passed | JSON report emitted. |
| `python scripts/validate_public_static_site.py` | passed | 8 pages; 9 source IDs checked. |
| `python scripts/validate_public_static_site.py --json` | passed | JSON report emitted. |
| `python scripts/check_github_pages_static_artifact.py` | passed | Static artifact valid; deployment unverified. |
| `python scripts/check_github_pages_static_artifact.py --json` | passed | JSON report emitted. |
| `python scripts/generate_public_alpha_rehearsal_evidence.py --check` | passed | Rehearsal evidence pack valid. |
| `python scripts/run_public_alpha_server.py --check-config` | passed | Public-alpha config valid; production flags false. |
| `python scripts/run_public_alpha_server.py --print-config-json` | passed | JSON config emitted. |
| `python scripts/public_alpha_smoke.py` | passed | 13/13 smoke checks passed. |
| `python site/build.py --check` | passed | Static site generator output valid. |
| `python site/build.py --json` | passed | JSON report emitted. |
| `python site/validate.py` | passed | 8 pages; dist validation valid. |
| `python site/validate.py --json` | passed | JSON report emitted. |
| `python scripts/generate_public_data_summaries.py --check` | passed | 6 data files valid. |
| `python scripts/generate_public_data_summaries.py --json` | passed | JSON report emitted. |
| `python scripts/generate_compatibility_surfaces.py --check` | passed | 18 lite/text/files surface files valid. |
| `python scripts/generate_compatibility_surfaces.py --json` | passed | JSON report emitted. |
| `python scripts/generate_static_resolver_demos.py --check` | passed | 8 demos valid. |
| `python scripts/generate_static_resolver_demos.py --json` | passed | JSON report emitted. |
| `python scripts/validate_static_host_readiness.py` | passed | Base paths valid; no root-relative links. |
| `python scripts/validate_static_host_readiness.py --json` | passed | JSON report emitted. |
| `python scripts/validate_live_backend_handoff.py` | passed | 11 reserved/registered endpoints; live capabilities disabled. |
| `python scripts/validate_live_backend_handoff.py --json` | passed | JSON report emitted. |
| `python scripts/validate_live_probe_gateway.py` | passed | 9 candidates disabled; wrapper live flags false. |
| `python scripts/validate_live_probe_gateway.py --json` | passed | JSON report emitted. |
| `python scripts/validate_compatibility_surfaces.py` | passed | 27 surfaces; 6 static implemented; 7 future disabled. |
| `python scripts/validate_compatibility_surfaces.py --json` | passed | JSON report emitted. |
| `python scripts/generate_static_snapshot.py --check` | passed | 12 snapshot files valid. |
| `python scripts/generate_static_snapshot.py --json` | passed | JSON report emitted. |
| `python scripts/validate_static_snapshot.py` | passed | 11 checksum entries valid. |
| `python scripts/validate_static_snapshot.py --json` | passed | JSON report emitted. |
| `python scripts/validate_snapshot_consumer_contract.py` | passed | 6 profiles; no production/native/relay consumer implemented. |
| `python scripts/validate_snapshot_consumer_contract.py --json` | passed | JSON report emitted. |
| `python scripts/validate_relay_surface_design.py` | passed | 11 protocol candidates; no relay/network/protocol server implemented. |
| `python scripts/validate_relay_surface_design.py --json` | passed | JSON report emitted. |
| `python scripts/validate_relay_prototype_plan.py` | passed | Local static HTTP first prototype planned; no runtime; approval required. |
| `python scripts/validate_relay_prototype_plan.py --json` | passed | JSON report emitted. |
| `python scripts/validate_native_client_contract.py` | passed | 9 lanes; first candidate Windows 7 WinForms; no GUI project files. |
| `python scripts/validate_native_client_contract.py --json` | passed | JSON report emitted. |
| `python scripts/validate_native_project_readiness_review.py` | passed | Ready for minimal skeleton only after human approval; no project files. |
| `python scripts/validate_native_project_readiness_review.py --json` | passed | JSON report emitted. |
| `python scripts/validate_windows_winforms_skeleton_plan.py` | passed | Planned path and namespace valid; no project files. |
| `python scripts/validate_windows_winforms_skeleton_plan.py --json` | passed | JSON report emitted. |
| `python scripts/validate_action_policy.py` | passed | 9 safe, 4 bounded, 15 future gated, 9 prohibited actions. |
| `python scripts/validate_action_policy.py --json` | passed | JSON report emitted. |
| `python scripts/validate_local_cache_privacy_policy.py` | passed | Privacy default local/private off; no cache/telemetry/accounts/cloud sync. |
| `python scripts/validate_local_cache_privacy_policy.py --json` | passed | JSON report emitted. |
| `python scripts/validate_external_baseline_observations.py` | passed | 64 queries; 192 global pending; 0 observed. |
| `python scripts/validate_external_baseline_observations.py --json` | passed | JSON report emitted. |
| `python scripts/report_external_baseline_status.py` | passed | Status ready; 192 pending; 0 observed. |
| `python scripts/report_external_baseline_status.py --json` | passed | JSON report emitted. |
| `python scripts/list_external_baseline_observations.py --batch batch_0` | passed | 39 Batch 0 pending slots listed. |
| `python scripts/list_external_baseline_observations.py --batch batch_0 --json` | passed | JSON report emitted. |
| `python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout` | passed | Pending manual observation template emitted; no observation recorded. |
| `python scripts/check_rust_source_registry_parity.py` | passed | Structure passed; Cargo skipped/unavailable; source count 9; cases 10. |
| `python scripts/check_rust_source_registry_parity.py --json` | passed | JSON report emitted. |
| `python scripts/validate_rust_local_index_parity_plan.py` | passed | 15 cases; 7 record kinds; no Rust local index implemented. |
| `python scripts/validate_rust_local_index_parity_plan.py --json` | passed | JSON report emitted. |
| `python scripts/check_rust_query_planner_parity.py` | passed | Structure passed; Cargo skipped/unavailable; cases 16. |
| `python scripts/check_rust_query_planner_parity.py --json` | passed | JSON report emitted. |
| `cargo --version` | unavailable | Cargo is not available in PATH. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo is not available in PATH. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo is not available in PATH. |
