# Command Results

| Command | Status | Notes |
| --- | --- | --- |
| `git status --short --branch` | passed | exit=0; duration=1.4s |
| `git log --oneline -n 20` | passed | exit=0; duration=0.2s |
| `git diff --check` | passed | exit=0; duration=0.2s |
| `python -m unittest discover -s tests/scripts -t .` | passed | exit=0; duration=28.6s |
| `python -m unittest discover -s tests/operations -t .` | passed | exit=0; duration=0.5s |
| `python -m unittest discover -s tests/hardening -t .` | passed | exit=0; duration=5.3s |
| `python -m unittest discover -s tests/parity -t .` | passed | exit=0; duration=1.2s |
| `python -m unittest discover -s tests/evals -t .` | passed | exit=0; duration=3.6s |
| `python -m unittest discover -s runtime -t .` | passed | exit=0; duration=4.7s |
| `python -m unittest discover -s surfaces -t .` | passed | exit=0; duration=28.3s |
| `python -m unittest discover -s tests -t .` | passed | exit=0; duration=39.3s |
| `python scripts/check_architecture_boundaries.py` | passed | exit=0; duration=0.7s |
| `python scripts/generate_python_oracle_golden.py --check` | passed | exit=0; duration=1.0s |
| `python scripts/run_archive_resolution_evals.py` | passed | exit=0; duration=0.5s |
| `python scripts/run_archive_resolution_evals.py --json` | passed | exit=0; duration=0.5s |
| `python scripts/run_search_usefulness_audit.py` | passed | exit=0; duration=0.9s |
| `python scripts/run_search_usefulness_audit.py --json` | passed | exit=0; duration=0.6s |
| `python scripts/validate_publication_inventory.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_publication_inventory.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/validate_public_static_site.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_public_static_site.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/check_github_pages_static_artifact.py` | passed | exit=0; duration=0.3s |
| `python scripts/check_github_pages_static_artifact.py --json` | passed | exit=0; duration=0.3s |
| `python scripts/generate_public_alpha_rehearsal_evidence.py --check` | passed | exit=0; duration=1.1s |
| `python scripts/run_public_alpha_server.py --check-config` | passed | exit=0; duration=0.4s |
| `python scripts/run_public_alpha_server.py --print-config-json` | passed | exit=0; duration=0.4s |
| `python scripts/public_alpha_smoke.py` | passed | exit=0; duration=0.7s |
| `python site/build.py --check` | passed | exit=0; duration=1.1s |
| `python site/build.py --json` | passed | exit=0; duration=1.0s |
| `python site/validate.py` | passed | exit=0; duration=0.3s |
| `python site/validate.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/generate_public_data_summaries.py --check` | passed | exit=0; duration=0.9s |
| `python scripts/generate_public_data_summaries.py --json` | passed | exit=0; duration=1.0s |
| `python scripts/generate_compatibility_surfaces.py --check` | passed | exit=0; duration=0.2s |
| `python scripts/generate_compatibility_surfaces.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/generate_static_resolver_demos.py --check` | passed | exit=0; duration=0.2s |
| `python scripts/generate_static_resolver_demos.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/validate_static_host_readiness.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_static_host_readiness.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/validate_live_backend_handoff.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_live_backend_handoff.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/validate_live_probe_gateway.py` | passed | exit=0; duration=0.3s |
| `python scripts/validate_live_probe_gateway.py --json` | passed | exit=0; duration=0.4s |
| `python scripts/validate_compatibility_surfaces.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_compatibility_surfaces.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/generate_static_snapshot.py --check` | passed | exit=0; duration=0.2s |
| `python scripts/generate_static_snapshot.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/validate_static_snapshot.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_static_snapshot.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/validate_external_baseline_observations.py` | passed | exit=0; duration=0.2s |
| `python scripts/validate_external_baseline_observations.py --json` | passed | exit=0; duration=0.3s |
| `python scripts/report_external_baseline_status.py` | passed | exit=0; duration=0.2s |
| `python scripts/report_external_baseline_status.py --json` | passed | exit=0; duration=0.2s |
| `python scripts/list_external_baseline_observations.py --batch batch_0` | passed | exit=0; duration=0.2s |
| `python scripts/list_external_baseline_observations.py --batch batch_0 --json` | passed | exit=0; duration=0.2s |
| `python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout` | passed | exit=0; duration=0.2s |
| `python scripts/check_rust_query_planner_parity.py` | passed | exit=0; duration=0.2s |
| `python scripts/check_rust_query_planner_parity.py --json` | passed | exit=0; duration=0.2s |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | tool unavailable: cargo |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | tool unavailable: cargo |
| `python scripts/validate_post_queue_checkpoint.py` | passed | post-generation focused checkpoint verification passed |
| `python scripts/validate_post_queue_checkpoint.py --json` | passed | post-generation focused checkpoint verification passed |
| `python -m unittest tests.operations.test_post_queue_state_checkpoint tests.scripts.test_validate_post_queue_checkpoint` | passed | post-generation focused checkpoint verification passed |
