# Command Results

P53 command evidence includes the initial clean repo checks, focused contract validation, the broad verification pass, one metadata-only drift repair for live-backend route reservations, and the final reruns that passed.

| Command | Status | Duration | Notes |
|---|---:|---:|---|
| `git status --short --branch` | pass | n/a | Initial P53 status was clean on main...origin/main. |
| `git rev-parse HEAD` | pass | n/a | Initial head bba9af03b2295311f4081ea489721c7372f68860. |
| `git rev-parse origin/main` | pass | n/a | Initial origin/main bba9af03b2295311f4081ea489721c7372f68860. |
| `git log --oneline -n 40` | pass | n/a | P50, P51, and P52 commits were present before P53 edits. |
| `python -m json.tool <modified schemas and P53 report>` | pass | n/a | Modified/new API schemas and P53 report parsed as JSON. |
| `python -m unittest runtime.gateway.tests.test_public_search_api runtime.gateway.tests.test_public_search_validation surfaces.web.tests.test_public_search_routes tests.scripts.test_public_search_smoke` | pass | n/a | Targeted local public-search runtime tests passed before the broad verification pass. |
| `python -m unittest tests.operations.test_public_search_production_contract tests.scripts.test_validate_public_search_production_contract` | pass | n/a | P53 focused validator/tests passed. |
| `python scripts/validate_live_backend_handoff.py --json (pre-repair)` | fail | n/a | Failed because P53 reserved /healthz and /status before the live-backend handoff validator allowed top-level wrapper routes; repaired as metadata-only drift. |
| `python scripts/validate_public_search_production_contract.py` | pass | 0.08s | P53 validator passed. |
| `python scripts/validate_public_search_production_contract.py --json` | pass | 0.08s | P53 validator JSON output parsed and reported status valid. |
| `python scripts/validate_static_deployment_evidence.py` | pass | 0.07s | P52 static deployment evidence validator still passes; Pages status remains unverified/operator-gated. |
| `python scripts/validate_post_p50_remediation.py` | pass | 0.07s | P51 remediation validator still passes. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | 0.08s | P50 platform audit validator still passes. |
| `python scripts/validate_public_search_contract.py` | pass | 0.08s | Existing public search API contract validator passes. |
| `python scripts/validate_public_search_contract.py --json` | pass | 0.08s | Existing public search API contract validator JSON output passes. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | 0.08s | Result-card contract validator passes. |
| `python scripts/validate_public_search_result_card_contract.py --json` | pass | 0.08s | Result-card contract validator JSON output passes. |
| `python scripts/validate_public_search_safety.py` | pass | 0.07s | Safety/abuse guard validator passes. |
| `python scripts/validate_public_search_safety.py --json` | pass | 0.08s | Safety/abuse guard validator JSON output passes. |
| `python scripts/validate_local_public_search_runtime.py` | pass | 0.08s | Local/prototype public-search runtime validator passes. |
| `python scripts/validate_local_public_search_runtime.py --json` | pass | 0.07s | Local/prototype public-search runtime validator JSON output passes. |
| `python scripts/public_search_smoke.py` | pass | 0.60s | Public search smoke passed 30/30. |
| `python scripts/public_search_smoke.py --json` | pass | 0.56s | Public search smoke JSON passed 30/30. |
| `python site/build.py --check` | pass | 1.02s | Static site build check passed. |
| `python site/build.py --json` | pass | 0.91s | Static site JSON build command passed. |
| `python site/validate.py` | pass | 0.16s | Static site validator passed. |
| `python scripts/validate_publication_inventory.py` | pass | 0.09s | Publication inventory validator passed. |
| `python scripts/validate_public_static_site.py` | pass | 0.10s | Public static site validator passed. |
| `python scripts/check_generated_artifact_drift.py` | pass | 6.99s | Generated artifact drift guard passed. |
| `python scripts/run_archive_resolution_evals.py` | pass | 0.37s | Archive-resolution eval runner passed; status_counts satisfied=6/6. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | 0.35s | Archive-resolution eval JSON passed; status_counts satisfied=6/6. |
| `python scripts/run_search_usefulness_audit.py` | pass | 0.38s | Search usefulness audit passed; covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | 0.40s | Search usefulness audit JSON passed with 64 total queries and no external observations recorded. |
| `python scripts/report_external_baseline_status.py --json` | pass | 0.07s | External baselines remain pending/manual: global 192 pending/0 observed; batch_0 39 pending. |
| `python -m unittest discover -s tests/scripts -t .` | fail | 62.17s | Initial run failed on live-backend handoff route-reservation drift; rerun passed after metadata-only validator/docs repair. |
| `python -m unittest discover -s tests/operations -t .` | pass | 3.97s | Operations tests passed. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 5.56s | Hardening tests passed. |
| `python -m unittest discover -s runtime -t .` | pass | 5.49s | Runtime tests passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 31.84s | Surface tests passed. |
| `python -m unittest discover -s tests -t .` | fail | 80.48s | Initial full repo tests failed on live-backend handoff route-reservation drift; rerun passed after metadata-only validator/docs repair. |
| `python scripts/check_architecture_boundaries.py` | pass | 0.56s | Architecture boundary checker passed. |
| `cargo --version` | unavailable | 0.02s | Cargo is unavailable in this environment; command was not treated as hidden success. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | 0.02s | Cargo is unavailable in this environment; optional Rust check could not run. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | 0.02s | Cargo is unavailable in this environment; optional Rust tests could not run. |
| `git diff --check` | pass | 0.11s | Whitespace diff check passed. |
| `git status --short --branch` | pass | 0.07s | Final pre-commit status had expected P53 modifications only. |
| `python scripts/validate_live_backend_handoff.py` | pass | 0.11s | Live-backend handoff validator passed after accepting P53 reserved top-level health/status and capability/absence routes as unhosted contract metadata. |
| `python scripts/validate_live_backend_handoff.py --json` | pass | 0.11s | Live-backend handoff validator JSON output passed after P53 metadata repair. |
| `python scripts/validate_public_search_production_contract.py` | pass | 0.08s | P53 validator passed. |
| `python scripts/validate_public_search_production_contract.py --json` | pass | 0.08s | P53 validator JSON output parsed and reported status valid. |
| `python scripts/check_generated_artifact_drift.py` | pass | 6.95s | Generated artifact drift guard passed. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 61.98s | Initial run failed on live-backend handoff route-reservation drift; rerun passed after metadata-only validator/docs repair. |
| `python -m unittest discover -s tests -t .` | pass | 79.63s | Initial full repo tests failed on live-backend handoff route-reservation drift; rerun passed after metadata-only validator/docs repair. |
| `git diff --check` | pass | 0.12s | Whitespace diff check passed. |
| `git status --short --branch` | pass | 0.07s | Final pre-commit status had expected P53 modifications only. |

Current factual counts from the final eval/audit pass:

- Archive-resolution evals: `satisfied=6`, `total=6`.
- Search usefulness audit: `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`, `total=64`.
- External baselines: `observed=0`, `pending_manual_observation=192`; Batch 0 remains `39` pending.
- Cargo/Rust optional checks: unavailable because `cargo` is not installed in this environment.
- GitHub Actions status: unverified; P53 did not query Actions status.
