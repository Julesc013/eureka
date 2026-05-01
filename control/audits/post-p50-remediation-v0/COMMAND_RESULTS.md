# Command Results

| Command | Status | Notes |
|---|---|---|
| `git status --short --branch` | pass | Initial P51 status was clean on `main...origin/main`. |
| `git rev-parse HEAD` | pass | Initial head: `d26d093897e5c7b09cf233c5a2771186009e8bfb`. |
| `git rev-parse origin/main` | pass | Initial origin/main matched `d26d093897e5c7b09cf233c5a2771186009e8bfb`. |
| `git log --oneline -n 20` | pass | P50 commits present. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | P50 audit pack valid. |
| `python scripts/validate_post_p49_platform_audit.py --json` | pass | JSON result parsed. |
| `python scripts/check_architecture_boundaries.py` | pass | 445 Python files checked, no violations. |
| `python scripts/run_archive_resolution_evals.py` | pass | 6 tasks, 6 satisfied. |
| `python scripts/run_search_usefulness_audit.py` | pass | 64 queries: covered 5, partial 40, source_gap 10, capability_gap 7, unknown 2. |
| `python scripts/report_external_baseline_status.py --json` | pass | 192 pending, 0 observed; batch_0 39 pending, 0 observed. |
| `cargo --version` | unavailable | Cargo not installed in current environment. |
| `python scripts/validate_source_pack.py --all-examples --json` | pass | 1/1 source pack example valid. |
| `python scripts/validate_evidence_pack.py --all-examples --json` | pass | 1/1 evidence pack example valid. |
| `python scripts/validate_index_pack.py --all-examples --json` | pass | 1/1 index pack example valid. |
| `python scripts/validate_contribution_pack.py --all-examples --json` | pass | 1/1 contribution pack example valid. |
| `python scripts/validate_master_index_review_queue.py --all-examples --json` | pass | 1/1 review queue example valid. |
| `python scripts/validate_pack_set.py --known-examples --json` | pass | 5/5 known examples passed. |
| `python scripts/validate_only_pack_import.py --known-examples --json` | pass | 5/5 validate-only examples passed; no mutation flags false. |
| `python -m unittest tests.scripts.test_validate_source_pack ... test_validate_only_pack_import` | pass | 54 focused pack validator tests passed. |
| `git diff --check` | pass | No whitespace errors; line-ending warnings only. |
| `python scripts/validate_post_p50_remediation.py` | pass | 17 required files checked. |
| `python scripts/validate_post_p50_remediation.py --json` | pass | JSON result parsed with 11 required remediation items. |
| `python site/build.py --check` | pass | Static site generator valid; `site/dist` current. |
| `python site/validate.py` | pass | 9 pages, dist validation valid. |
| `python scripts/validate_publication_inventory.py` | pass | 49 registered routes, 9 current static artifact pages. |
| `python scripts/validate_public_static_site.py` | pass | 9 pages and 15 source IDs checked. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | Static artifact valid; no deployment success claimed. |
| `python scripts/check_generated_artifact_drift.py` | pass | 10/10 artifact groups passed. |
| `python scripts/validate_public_search_contract.py` | pass | `local_index_only` first allowed mode; 6 routes registered. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | 5 examples checked. |
| `python scripts/validate_public_search_safety.py` | pass | Safety guard valid; telemetry default off. |
| `python scripts/validate_local_public_search_runtime.py` | pass | Local prototype backend valid; hosted deployment false. |
| `python scripts/public_search_smoke.py` | pass | 30/30 checks passed, including 14 blocked unsafe requests. |
| `python scripts/validate_pack_set.py --all-examples` | pass | 5/5 examples passed; no mutation flags false. |
| `python scripts/validate_only_pack_import.py --all-examples` | pass | 5/5 validate-only examples passed; no mutation flags false. |
| `python scripts/validate_local_quarantine_staging_model.py` | pass | No staging runtime or local-state roots present. |
| `python scripts/validate_staging_report_path_contract.py` | pass | Report path contract valid; no staging runtime. |
| `python scripts/validate_local_staging_manifest.py --all-examples` | pass | 1/1 synthetic manifest passed. |
| `python scripts/inspect_staged_pack.py --all-examples` | pass | Read-only inspection passed; no mutation flags false. |
| `python scripts/validate_ai_provider_contract.py` | pass | Disabled stub provider valid; no model/network calls. |
| `python scripts/validate_ai_output.py --all-examples` | pass | 4/4 typed AI examples passed; no model calls. |
| `python scripts/validate_ai_assisted_drafting_plan.py` | pass | Planning/example-only AI drafting plan valid; no runtime. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | 6/6 archive eval tasks satisfied. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | Counts remained covered 5, partial 40, source_gap 10, capability_gap 7, unknown 2. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | 40 Python-oracle golden files current. |
| `python -m unittest discover -s tests/scripts -t .` | fail then pass | First run exposed repository-layout wording drift in `LICENSE_SELECTION_REQUIRED.md`; after replacing the stale `third-party` token, 225 tests passed. |
| `python -m unittest discover -s tests/operations -t .` | pass | 396 tests passed. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 53 tests passed. |
| `python -m unittest discover -s tests/parity -t .` | pass | 25 tests passed. |
| `python -m unittest discover -s tests/evals -t .` | pass | 45 tests passed. |
| `python -m unittest discover -s runtime -t .` | pass | 320 tests passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 168 tests passed. |
| `python -m unittest discover -s tests -t .` | pass | 790 tests passed. |
| `python scripts/check_architecture_boundaries.py` | pass | 445 Python files checked, no violations. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo command not found. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo command not found. |
