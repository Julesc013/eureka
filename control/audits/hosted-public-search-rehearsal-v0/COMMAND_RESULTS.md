# Command Results

P58 command results are local-only rehearsal evidence. They do not prove hosted deployment, edge rate limits, live source coverage, or production readiness.

| Command | Status | Duration | Notes |
| --- | --- | --- | --- |
| `git status --short --branch` | pass | n/a | Initial P58 checkout was clean on main...origin/main. |
| `git rev-parse HEAD` | pass | n/a | Initial P58 head 35c99aafa60d625d3d9baa16f2575e7f8bb50805. |
| `git rev-parse origin/main` | pass | n/a | origin/main matched initial P58 head. |
| `git log --oneline -n 50` | pass | n/a | P50 through P57 commits were present. |
| `python scripts/run_hosted_public_search_rehearsal.py` | pass | 1052 ms | Hosted local rehearsal passed 60/60 checks: 9 routes, 5 safe queries, 34/34 blocked requests, 584 public-index documents. |
| `python scripts/run_hosted_public_search_rehearsal.py --json` | pass | 990 ms | JSON rehearsal evidence parsed successfully. |
| `python scripts/validate_hosted_public_search_rehearsal.py` | pass | 1016 ms | P58 audit pack and live local rehearsal validation passed. |
| `python scripts/validate_hosted_public_search_rehearsal.py --json` | pass | 1068 ms | P58 validator JSON parsed successfully. |
| `python scripts/run_public_search_safety_evidence.py` | pass | 410 ms | P57 safety evidence still passed. |
| `python scripts/validate_public_search_safety_evidence.py` | pass | 438 ms | P57 safety evidence validator still passed. |
| `python scripts/validate_static_site_search_integration.py` | pass | 61 ms | P56 static handoff remains backend_unconfigured and valid. |
| `python scripts/validate_public_search_index_builder.py` | pass | 810 ms | P55 index builder report remains valid; document_count 584. |
| `python scripts/validate_public_search_index.py` | pass | 258 ms | Public index remains valid with no private paths detected. |
| `python scripts/validate_hosted_public_search_wrapper.py` | pass | 275 ms | P54 wrapper validator remains valid and undeployed/unverified. |
| `python scripts/check_hosted_public_search_wrapper.py` | pass | 265 ms | P54 in-process wrapper check passed. |
| `python scripts/run_hosted_public_search.py --check-config` | pass | 217 ms | Hosted wrapper safe config check passed. |
| `python scripts/validate_public_search_production_contract.py` | pass | 57 ms | P53 production-facing contract remains valid after P58 docs. |
| `python scripts/validate_static_deployment_evidence.py` | pass | 56 ms | P52 static deployment evidence remains valid/unverified. |
| `python scripts/validate_post_p50_remediation.py` | pass | 64 ms | P51 remediation pack remains valid. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | 77 ms | P50 platform audit pack remains valid. |
| `python scripts/validate_public_search_contract.py` | pass | 66 ms | Public search API contract validator passed. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | 60 ms | Public result-card contract validator passed. |
| `python scripts/validate_public_search_safety.py` | pass | 56 ms | Public search safety validator passed. |
| `python scripts/validate_local_public_search_runtime.py` | pass | 55 ms | Local public search runtime validator passed. |
| `python scripts/public_search_smoke.py` | pass | 545 ms | Public search smoke passed. |
| `python scripts/public_search_smoke.py --json` | pass | 542 ms | Public search smoke JSON parsed. |
| `python scripts/build_public_search_index.py --check` | pass | 482 ms | Public search index build drift check passed. |
| `python site/build.py --check` | pass | 964 ms | Static site build check passed. |
| `python site/validate.py` | pass | 85 ms | Static site validation passed. |
| `python scripts/validate_publication_inventory.py` | pass | 64 ms | Publication inventory validation passed. |
| `python scripts/validate_public_static_site.py` | pass | 105 ms | Public static site validation passed. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | 153 ms | site/dist static artifact check passed; no deployment claim made. |
| `python scripts/check_generated_artifact_drift.py` | pass | 9347 ms | Generated artifact drift guard passed. |
| `python scripts/public_alpha_smoke.py` | pass | 622 ms | Public alpha smoke passed. |
| `python scripts/run_archive_resolution_evals.py` | pass | 328 ms | Archive resolution evals passed: satisfied=6. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | 328 ms | Archive resolution eval JSON parsed. |
| `python scripts/run_search_usefulness_audit.py` | pass | 357 ms | Search usefulness audit passed: covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | 383 ms | Search usefulness JSON parsed. |
| `python scripts/report_external_baseline_status.py --json` | pass | 54 ms | External baseline status parsed; observations remain manual pending. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | 920 ms | Python oracle golden drift check passed. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 75951 ms | tests/scripts unittest lane passed. |
| `python -m unittest discover -s tests/operations -t .` | pass | 8014 ms | tests/operations unittest lane passed. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 5448 ms | tests/hardening unittest lane passed. |
| `python -m unittest discover -s tests/parity -t .` | pass | 1568 ms | tests/parity unittest lane passed. |
| `python -m unittest discover -s runtime -t .` | pass | 4765 ms | runtime unittest lane passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 30910 ms | surfaces unittest lane passed. |
| `python -m unittest discover -s tests -t .` | pass | 98472 ms | Full tests unittest discovery lane passed. |
| `python scripts/check_architecture_boundaries.py` | pass | 512 ms | Architecture boundary checker passed. |
| `git diff --check` | pass | 81 ms | No whitespace/conflict-marker issues detected. |
| `docker --version` | unavailable_or_failed_optional | 271 ms | Docker executable unavailable in this environment; optional Docker build was not attempted. |
| `cargo --version` | unavailable_or_failed_optional | 24 ms | Cargo executable unavailable in this environment. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable_or_failed_optional | 25 ms | Cargo executable unavailable; workspace check not run. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable_or_failed_optional | 23 ms | Cargo executable unavailable; workspace tests not run. |
| `git status --short --branch` | pass | 44 ms | Worktree contained P58 edits at verification time. |
