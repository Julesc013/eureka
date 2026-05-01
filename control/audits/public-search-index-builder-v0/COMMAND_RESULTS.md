# Command Results

| Command | Status | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | Initial P55 status was clean on `main...origin/main`. |
| `git rev-parse HEAD` | pass | Initial head `e11d95b02c60906920d66703b7fd5248d68c1243`. |
| `git rev-parse origin/main` | pass | Initial origin/main matched head. |
| `git log --oneline -n 50` | pass | P50 through P54 commits were present. |
| `python scripts/build_public_search_index.py --rebuild` | pass | Generated 584 documents under `data/public_index`. |
| `python scripts/build_public_search_index.py --check` | pass | Committed artifacts matched regenerated temp artifacts. |
| `python scripts/build_public_search_index.py --json` | pass | Preview JSON parsed; no repo mutation. |
| `python scripts/validate_public_search_index.py` | pass | Public index artifacts valid. |
| `python scripts/validate_public_search_index.py --json` | pass | JSON validator output parsed with status valid. |
| `python scripts/validate_public_search_index_builder.py` | pass | P55 audit pack, artifacts, docs, drift entry, and hard false booleans validated. |
| `python scripts/validate_public_search_index_builder.py --json` | pass | JSON validator output parsed with status valid. |
| `python scripts/check_generated_artifact_drift.py --artifact public_search_index` | pass | Public search index check and validators passed. |
| `python scripts/check_generated_artifact_drift.py` | pass | All 11 generated artifact groups passed, including `public_search_index`. |
| `python scripts/run_hosted_public_search.py --check-config` | pass | Hosted wrapper config accepted safe env and present public index. |
| `python scripts/check_hosted_public_search_wrapper.py` and `--json` | pass | Hosted wrapper local rehearsal passed 14/14 and JSON parsed. |
| `python scripts/validate_hosted_public_search_wrapper.py` | pass | P54 wrapper validator still passes. |
| `python scripts/validate_public_search_production_contract.py` | pass | P53 production contract validator still passes. |
| `python scripts/validate_public_search_contract.py` and `--json` | pass | Public search API contract remains valid. |
| `python scripts/validate_public_search_result_card_contract.py` and `--json` | pass | Result-card contract remains valid. |
| `python scripts/validate_public_search_safety.py` and `--json` | pass | Safety guard remains valid. |
| `python scripts/validate_local_public_search_runtime.py` and `--json` | pass | Local public search runtime remains valid. |
| `python scripts/public_search_smoke.py` and `--json` | pass | Public search smoke passed 30/30. |
| `python scripts/public_alpha_smoke.py` | pass | Public alpha smoke passed 18/18. |
| `python site/build.py --check` | pass | Static site generator check valid. |
| `python site/validate.py` | pass | Static site validation valid for 9 pages. |
| `python scripts/validate_publication_inventory.py` | pass | Publication inventory valid. |
| `python scripts/validate_public_static_site.py` | pass | Public static site valid; 15 source ids checked. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | GitHub Pages static artifact valid locally; no deployment evidence claimed. |
| `python scripts/run_archive_resolution_evals.py` and `--json` | pass | Archive resolution hard evals remain `satisfied=6`. |
| `python scripts/run_search_usefulness_audit.py` and `--json` | pass | Counts remain `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`. |
| `python scripts/report_external_baseline_status.py --json` | pass | External baselines remain 192 pending / 0 observed; Batch 0 remains 39 pending / 0 observed. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | Python oracle golden fixture pack passed with 40 files. |
| `python -m unittest discover -s tests/scripts -t .` | failed_then_fixed | Initial run found stale drift-guard expected count 10 vs 11; repaired the test and reran successfully. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 239 tests passed after repair. |
| `python -m unittest discover -s tests/operations -t .` | pass | 418 tests passed. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 53 tests passed. |
| `python -m unittest discover -s tests/parity -t .` | pass | 25 tests passed. |
| `python -m unittest discover -s runtime -t .` | pass | 320 tests passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 168 tests passed. |
| `python -m unittest discover -s tests -t .` | pass | 826 tests passed. |
| `python scripts/check_architecture_boundaries.py` | pass | 446 Python files checked; no boundary violations. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | P50 validator passed. |
| `python scripts/validate_post_p50_remediation.py` | pass | P51 validator passed. |
| `python scripts/validate_static_deployment_evidence.py` | pass | P52 validator passed; deployment remains unverified/operator-gated. |
| `cargo --version` | unavailable | Cargo is not installed or not on PATH in this environment. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo is not installed or not on PATH in this environment. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo is not installed or not on PATH in this environment. |
| `git diff --check` | pass | Passed; PowerShell/Git emitted CRLF normalization warnings only. |
