# Command Results

Final P56 command results:

| Command | Status | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | Initial P56 checkout was main...origin/main; final pre-commit status had expected P56 edits. |
| `git rev-parse HEAD` | pass | Initial P56 head e9bfbf0b41966c56f02311fc9448e6182cc95770. |
| `git rev-parse origin/main` | pass | origin/main matched the initial head. |
| `git log --oneline -n 50` | pass | P50 through P55 commits were present. |
| `python site/build.py --json` | pass | Generated P56 search config, public index summary, and static search surfaces. |
| `python scripts/generate_public_data_summaries.py --check` | pass | Public data summaries matched generated outputs. |
| `python scripts/generate_compatibility_surfaces.py --check` | pass | Lite/text/files surfaces matched generated outputs. |
| `python site/validate.py` | pass | Static site validation passed. |
| `python site/validate.py --json` | pass | Static site JSON validation passed. |
| `python scripts/validate_public_static_site.py` | pass | Public static site validation passed. |
| `python scripts/validate_publication_inventory.py` | pass | Publication inventory validation passed with 51 routes and 14 required public data paths. |
| `python scripts/validate_public_data_stability.py` | pass | Public data stability validation passed after adding search_config and public_index_summary. |
| `python scripts/validate_static_site_search_integration.py` | pass | P56 validator passed. |
| `python scripts/validate_static_site_search_integration.py --json` | pass | P56 validator JSON passed; document_count=584; backend_unconfigured; search_form_enabled=false. |
| `python scripts/check_generated_artifact_drift.py --artifact static_search_integration` | pass | Static search integration drift guard passed. |
| `python scripts/check_generated_artifact_drift.py` | pass | Full drift guard passed after regenerating the static snapshot example for new public data/page registry metadata. |
| `python scripts/generate_static_snapshot.py --update --json` | pass | Repaired bounded generated snapshot drift caused by new static search data/page registry entries. |
| `python scripts/build_public_search_index.py --check` | pass | Public search index check passed; document_count=584; fallback enabled. |
| `python scripts/validate_public_search_index.py` | pass | Public search index validation passed; no private paths detected. |
| `python scripts/validate_public_search_index_builder.py` | pass | P55 index builder validator passed. |
| `python scripts/run_hosted_public_search.py --check-config` | pass | Hosted wrapper safe defaults passed; local_index_only and hard safety flags false. |
| `python scripts/check_hosted_public_search_wrapper.py` | pass | Hosted wrapper local rehearsal passed 14/14 checks. |
| `python scripts/validate_hosted_public_search_wrapper.py` | pass | Hosted wrapper validator passed; backend deployed/verified false. |
| `python scripts/validate_public_search_production_contract.py` | pass | P53 public search production contract validator passed. |
| `python scripts/validate_static_deployment_evidence.py` | pass | P52 static deployment evidence validator passed; deployment_verified false. |
| `python scripts/validate_post_p50_remediation.py` | pass | P51 remediation validator passed. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | P50 platform audit validator passed. |
| `python scripts/validate_public_search_contract.py` | pass | Public search contract validator passed. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | Public result card contract validator passed. |
| `python scripts/validate_public_search_safety.py` | pass | Public search safety validator passed; max query length 160; telemetry default off. |
| `python scripts/validate_local_public_search_runtime.py` | pass | Local public search runtime validator passed; local_index_only; hosted deployment false. |
| `python scripts/public_search_smoke.py` | pass | Public search smoke passed 30/30 checks. |
| `python scripts/public_search_smoke.py --json` | pass | Public search smoke JSON passed; safe queries 9; blocked requests 14. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | GitHub Pages static artifact check passed locally for site/dist. |
| `python scripts/public_alpha_smoke.py` | pass | Public alpha smoke passed 18/18 checks. |
| `python scripts/run_archive_resolution_evals.py` | pass | Archive resolution evals passed: satisfied=6. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | Archive resolution eval JSON passed: satisfied=6. |
| `python scripts/run_search_usefulness_audit.py` | pass | Search usefulness audit passed: covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | Search usefulness audit JSON passed with the same status counts. |
| `python scripts/report_external_baseline_status.py --json` | pass | External baseline status valid: 192 pending, 0 observed; batch_0 39 pending, 0 observed. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | Python oracle golden check passed. |
| `python -m unittest discover -s tests/scripts -t .` | pass | Ran 241 tests; OK. |
| `python -m unittest discover -s tests/operations -t .` | pass | Ran 425 tests; OK. |
| `python -m unittest discover -s tests/hardening -t .` | pass | Ran 53 tests; OK. |
| `python -m unittest discover -s tests/parity -t .` | pass | Ran 25 tests; OK. |
| `python -m unittest discover -s runtime -t .` | pass | Ran 320 tests; OK. |
| `python -m unittest discover -s surfaces -t .` | pass | Ran 168 tests; OK. |
| `python -m unittest discover -s tests -t .` | pass | Ran 835 tests; OK. |
| `python scripts/check_architecture_boundaries.py` | pass | Checked 446 Python files; no boundary violations. |
| `git diff --check` | pass | No whitespace errors; Git reported line-ending conversion warnings only. |
| `cargo --version` | unavailable | Optional Rust toolchain check unavailable: cargo command not found. |

Notes:

- `python scripts/check_generated_artifact_drift.py` initially found static snapshot example drift after P56 added new public data/page registry metadata. The drift was bounded generated-artifact drift and was repaired with `python scripts/generate_static_snapshot.py --update --json`.
- GitHub Pages deployment status was not verified by P56; local `site/dist` artifact validation passed, but hosted Pages evidence remains operator-gated unless a later audit records real workflow/deployment evidence.
- Cargo is unavailable in this environment and is recorded as optional/unavailable, not as a hidden pass.
