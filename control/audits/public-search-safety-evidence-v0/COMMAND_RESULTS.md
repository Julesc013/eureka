# Command Results

P57 command results are local/public-alpha evidence only. They do not prove hosted deployment, edge rate limits, live source coverage, or production readiness.

| Command | Status | Duration | Notes |
| --- | --- | --- | --- |
| `git status --short --branch` | pass | n/a | Initial P57 checkout was clean on main...origin/main before edits; final status is recorded separately. |
| `git rev-parse HEAD` | pass | n/a | Initial P57 head ca72fc7859b3eafc86d06db395d6a363ea75d8b9. |
| `git rev-parse origin/main` | pass | n/a | origin/main matched initial head. |
| `git log --oneline -n 50` | pass | n/a | P50 through P56 commits were present; P56 head was ca72fc7 before P57 work. |
| `python scripts/run_public_search_safety_evidence.py` | pass | 412 ms | Passed 64/64 checks: 9 safe routes, 4 safe queries, 32/32 blocked requests, 584 public-index documents reviewed. |
| `python scripts/run_public_search_safety_evidence.py --json` | pass | 419 ms | JSON evidence parsed; all hard booleans remained false. |
| `python scripts/validate_public_search_safety_evidence.py` | pass | 409 ms | P57 audit pack and local safety evidence validated. |
| `python scripts/validate_public_search_safety_evidence.py --json` | pass | 418 ms | Validator JSON parsed; 12 forbidden categories covered. |
| `python scripts/validate_static_site_search_integration.py` | pass | 57 ms | P56 static handoff remained valid; backend_unconfigured and document_count 584. |
| `python scripts/validate_public_search_index_builder.py` | pass | 785 ms | P55 index-builder pack remained valid; document_count 584. |
| `python scripts/validate_public_search_index.py` | pass | 293 ms | Public index remained valid with no private paths detected. |
| `python scripts/validate_hosted_public_search_wrapper.py` | pass | 283 ms | P54 hosted wrapper remained local_index_only and undeployed/unverified. |
| `python scripts/check_hosted_public_search_wrapper.py` | pass | 267 ms | Hosted-wrapper local rehearsal passed. |
| `python scripts/run_hosted_public_search.py --check-config` | pass | 215 ms | Safe hosted-wrapper config passed under defaults. |
| `python scripts/validate_public_search_production_contract.py` | pass | 57 ms | P53 production contract remained valid. |
| `python scripts/validate_static_deployment_evidence.py` | pass | 55 ms | P52 static deployment evidence pack remained valid. |
| `python scripts/validate_post_p50_remediation.py` | pass | 56 ms | P51 remediation pack remained valid. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | 55 ms | P50 audit pack remained valid. |
| `python scripts/validate_public_search_contract.py` | pass | 62 ms | Public search API contract validator passed. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | 57 ms | Public result-card contract validator passed. |
| `python scripts/validate_public_search_safety.py` | pass | 58 ms | Existing public search safety validator passed. |
| `python scripts/validate_local_public_search_runtime.py` | pass | 55 ms | Local public search runtime validator passed. |
| `python scripts/public_search_smoke.py` | pass | 544 ms | Public search smoke passed 30/30 checks with 9 safe queries and 14 blocked requests. |
| `python scripts/public_search_smoke.py --json` | pass | 553 ms | Public search smoke JSON parsed. |
| `python scripts/build_public_search_index.py --check` | pass | 485 ms | Public search index build drift check passed. |
| `python site/build.py --check` | pass | 950 ms | Static site build check passed. |
| `python site/validate.py` | pass | 85 ms | Static site validation passed. |
| `python scripts/validate_publication_inventory.py` | pass | 65 ms | Publication inventory validation passed. |
| `python scripts/validate_public_static_site.py` | pass | 81 ms | Public static site validation passed. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | 152 ms | site/dist static artifact check passed; no deployment evidence claimed. |
| `python scripts/check_generated_artifact_drift.py` | pass | 9455 ms | Generated artifact drift guard passed for all 12 artifact groups. |
| `python scripts/public_alpha_smoke.py` | pass | 634 ms | Public alpha smoke passed 18/18 checks. |
| `python scripts/run_archive_resolution_evals.py` | pass | 330 ms | Archive resolution evals passed: 6/6 satisfied. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | 354 ms | Archive resolution eval JSON parsed; satisfied=6. |
| `python scripts/run_search_usefulness_audit.py` | pass | 364 ms | Search usefulness audit passed: covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | 401 ms | Search usefulness JSON parsed with all external baseline observations pending. |
| `python scripts/report_external_baseline_status.py --json` | pass | 56 ms | External baseline status parsed; batch_0 remains 39/39 pending manual observation. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | 917 ms | Python oracle golden drift check passed. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 71631 ms | tests/scripts unittest lane passed. |
| `python -m unittest discover -s tests/operations -t .` | pass | 7018 ms | tests/operations unittest lane passed. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 5497 ms | tests/hardening unittest lane passed. |
| `python -m unittest discover -s tests/parity -t .` | pass | 1472 ms | tests/parity unittest lane passed. |
| `python -m unittest discover -s runtime -t .` | pass | 4737 ms | runtime unittest lane passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 30659 ms | surfaces unittest lane passed. |
| `python -m unittest discover -s tests -t .` | pass | 93081 ms | Full tests unittest discovery lane passed. |
| `python scripts/check_architecture_boundaries.py` | pass | 538 ms | Architecture boundary checker passed. |
| `git diff --check` | pass | 81 ms | No whitespace/conflict-marker issues detected. |
| `cargo --version` | unavailable_or_failed_optional | 289 ms | Cargo executable unavailable in this environment; recorded as optional/unavailable. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable_or_failed_optional | 23 ms | Cargo executable unavailable in this environment; workspace check not run. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable_or_failed_optional | 22 ms | Cargo executable unavailable in this environment; workspace tests not run. |
| `git status --short --branch` | pass | 48 ms | Worktree still contained P57 edits at verification time. |
