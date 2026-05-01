# Command Results

| Command | Status | Duration | Notes |
|---|---:|---:|---|
| `git status --short --branch` | pass | not measured | Initial P52 status was clean on `main...origin/main`. |
| `git rev-parse HEAD` | pass | not measured | `9bbb451ed23b5a5725f1ca0592f19a0edd6fecc5`. |
| `git rev-parse origin/main` | pass | not measured | `9bbb451ed23b5a5725f1ca0592f19a0edd6fecc5`. |
| `git log --oneline -n 30` | pass | not measured | P51 commits present. |
| `Get-Content .github/workflows/pages.yml` | pass | not measured | Workflow uploads `site/dist`. |
| `Get-Content control/inventory/publication/deployment_targets.json` | pass | not measured | GitHub Pages target is static and unverified. |
| `Get-Content docs/operations/GITHUB_PAGES_DEPLOYMENT.md` | pass | not measured | Operator steps and static-only posture present. |
| `python site/build.py --check` | pass | 1.4s | Static generator check valid. |
| `python site/build.py --json` | pass | 1.1s | Mutating build completed; status valid. |
| `python site/validate.py` | transient_fail_then_pass | 0.5s | Concurrent first run observed transient missing generated files while build was mutating; serial rerun passed. |
| `python site/validate.py --json` | transient_fail_then_pass | 0.5s | Concurrent first run invalid; serial rerun passed with 7 data files, 21 compatibility files, 11 demo files. |
| `python scripts/validate_publication_inventory.py` | pass | 0.4s | 49 registered routes. |
| `python scripts/validate_public_static_site.py` | transient_fail_then_pass | 0.5s | Concurrent first run invalid; serial rerun passed. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | 0.5s | Artifact valid. |
| `python scripts/check_generated_artifact_drift.py --artifact static_site_dist` | pass | 1.7s | `static_site_dist` group passed. |
| `git remote -v` | pass | not measured | `origin` points to `https://github.com/Julesc013/eureka.git`. |
| `gh --version` | unavailable | not measured | `gh` command not found. |
| `gh auth status` | unavailable | not measured | `gh` command not found. |
| `gh workflow list` | unavailable_skipped | not measured | Skipped because `gh` is unavailable. |
| `gh run list --workflow pages.yml --limit 10` | unavailable_skipped | not measured | Skipped because `gh` is unavailable. |
| `gh api repos/Julesc013/eureka/pages` | unavailable_skipped | not measured | Skipped because `gh` is unavailable. |
| `Get-Content control/audits/github-pages-run-evidence-v0/RUN_EVIDENCE.md` | pass | not measured | Prior run evidence records failure at Configure GitHub Pages. |
| `Get-Content control/audits/github-pages-run-evidence-v0/DEPLOYMENT_EVIDENCE.md` | pass | not measured | Prior deployment record failed; no URL. |
| `Get-Content control/audits/github-pages-run-evidence-v0/github_pages_run_evidence_report.json` | pass | not measured | Prior Pages API status `404_not_found`. |
| `Get-Content control/audits/github-pages-run-evidence-v0/GITHUB_ACTIONS_RUN.md` | unavailable | not measured | File does not exist; actual file is `RUN_EVIDENCE.md`. |
| `Get-Content control/audits/github-pages-run-evidence-v0/DEPLOYMENT_STATUS.md` | unavailable | not measured | File does not exist; actual file is `DEPLOYMENT_EVIDENCE.md`. |
| `python scripts/validate_static_deployment_evidence.py` | pass | not measured | P52 audit pack valid; deployment remains unverified and not claimed. |
| `python scripts/validate_static_deployment_evidence.py --json` | pass | not measured | JSON validator output parsed; status `valid`. |
| `python scripts/validate_post_p50_remediation.py` | pass | not measured | P51 remediation pack still validates. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | not measured | P50 platform audit pack still validates. |
| `python scripts/check_generated_artifact_drift.py` | pass | not measured | 10/10 generated artifact groups passed. |
| `python scripts/validate_public_search_contract.py` | pass | not measured | Public search contract valid. |
| `python scripts/validate_public_search_result_card_contract.py` | pass | not measured | Result card contract valid. |
| `python scripts/validate_public_search_safety.py` | pass | not measured | Safety/abuse guard valid. |
| `python scripts/validate_local_public_search_runtime.py` | pass | not measured | Local prototype runtime valid; hosted deployment false. |
| `python scripts/public_search_smoke.py` | pass | not measured | 30/30 checks passed; 9 safe queries, 14 blocked requests. |
| `python scripts/public_alpha_smoke.py` | pass | not measured | 18/18 checks passed. |
| `python scripts/run_archive_resolution_evals.py` | pass | not measured | 6 tasks satisfied. |
| `python scripts/run_archive_resolution_evals.py --json` | pass | not measured | JSON output produced; 6 tasks satisfied. |
| `python scripts/run_search_usefulness_audit.py` | pass | not measured | 64 queries: covered 5, partial 40, source_gap 10, capability_gap 7, unknown 2. |
| `python scripts/run_search_usefulness_audit.py --json` | pass | not measured | JSON output produced for the same 64-query audit. |
| `python scripts/report_external_baseline_status.py --json` | pass | not measured | 192 pending / 0 observed; batch_0 39 pending / 0 observed. |
| `python -m unittest discover -s tests/scripts -t .` | pass | 72.7s | 227 tests passed. |
| `python -m unittest discover -s tests/operations -t .` | pass | previously measured | 402 tests passed earlier in the P52 run. |
| `python -m unittest discover -s tests/hardening -t .` | pass | previously measured | 53 tests passed earlier in the P52 run. |
| `python -m unittest discover -s runtime -t .` | pass | 6.8s | 320 tests passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 37.9s | 168 tests passed. |
| `python -m unittest discover -s tests -t .` | pass | 89.7s | 798 tests passed. |
| `python scripts/check_architecture_boundaries.py` | pass | 0.9s | 445 Python files checked; no boundary violations. |
| `cargo --version` | unavailable | not measured | `cargo` command not found. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | not measured | `cargo` command not found. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | not measured | `cargo` command not found. |
| `git diff --check` | pass | 0.3s | No whitespace errors; PowerShell reported expected LF-to-CRLF working-copy warnings. |
| `git status --short --branch` | pass | 0.3s | Working tree contains only P52 edits before commit. |
