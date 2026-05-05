# Command Results

P85 focused validation:

- `python scripts/validate_compatibility_target_profile.py --all-examples`: passed; 6 profiles valid.
- `python scripts/validate_compatibility_target_profile.py --all-examples --json`: passed.
- `python scripts/validate_compatibility_aware_ranking_assessment.py --all-examples`: passed; 6 assessments valid.
- `python scripts/validate_compatibility_aware_ranking_assessment.py --all-examples --json`: passed.
- `python scripts/validate_compatibility_explanation.py --all-examples`: passed; 6 explanations valid.
- `python scripts/validate_compatibility_explanation.py --all-examples --json`: passed.
- `python scripts/validate_compatibility_aware_ranking_contract.py`: passed.
- `python scripts/validate_compatibility_aware_ranking_contract.py --json`: passed.
- `python scripts/dry_run_compatibility_aware_ranking.py --target-os "Windows 7 x64" --left-title "Strong compatibility evidence result" --right-title "Unknown compatibility result" --json`: passed; stdout-only dry run, no files written.

Related contract validation:

- Evidence-weighted ranking, result-merge/deduplication, identity-resolution, comparison-page, source-page, and object-page validators passed where present.
- Connector approval validators for Software Heritage, npm, PyPI, GitHub Releases, Wayback/CDX/Memento, and Internet Archive metadata passed as approval-only examples.
- Source cache/evidence ledger, source sync worker, candidate index, candidate promotion, known absence, and query-intelligence contract validators passed where present.

Public search/static/eval lanes:

- `python scripts/public_search_smoke.py` and `--json`: passed; 30/30 checks, local-index-only, downloads/installs/uploads/live probes disabled.
- `python scripts/build_public_search_index.py --check`: passed; 584 public-index documents, fallback enabled, no index mutation.
- `python site/build.py --check`, `python site/validate.py`, `python scripts/validate_publication_inventory.py`, `python scripts/validate_public_static_site.py`, `python scripts/check_github_pages_static_artifact.py --path site/dist`: passed.
- `python scripts/check_generated_artifact_drift.py`: passed after correcting the P85 audit backlog entry into the repo's JSON-style AIDE backlog.
- `python scripts/public_alpha_smoke.py`: passed; 18/18 checks.
- `python scripts/run_archive_resolution_evals.py` and `--json`: passed; 6/6 tasks satisfied in local-index mode.
- `python scripts/run_search_usefulness_audit.py` and `--json`: passed; 64 queries with coverage/gap status preserved.
- `python scripts/report_external_baseline_status.py --json`: passed; manual external observations remain pending.
- `python scripts/generate_python_oracle_golden.py --check`: passed.

Unit and boundary lanes:

- `python -m unittest discover -s tests/scripts -t .`: passed; 586 tests.
- `python -m unittest discover -s tests/operations -t .`: passed; 553 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed; 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed; 25 tests.
- `python -m unittest discover -s runtime -t .`: passed; 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed; 168 tests.
- `python -m unittest discover -s tests -t .`: passed; 1308 tests.
- `python scripts/check_architecture_boundaries.py`: passed; 446 Python files checked.
- `git diff --check`: passed; CRLF warnings only.

Hosted/baseline status:

- `python scripts/verify_public_hosted_deployment.py --from-repo-config --json`: completed without deployment claims; hosted backend is not configured and configured static GitHub Pages checks returned 404, so deployment remains unverified/operator-gated.
- `python scripts/validate_public_hosted_deployment_evidence.py`: passed with warnings preserving the hosted-deployment gate.
- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`: passed as ineligible for comparison because observed manual baselines are 0 and pending observations are 39.
- `python scripts/validate_external_baseline_comparison_report.py`: passed; no external comparison claim made.

Optional:

- `cargo --version`: unavailable in this environment, so optional Rust checks were not run.
