# Command Results

Verification was run locally from `d:\Projects\Eureka\eureka` on 2026-05-05. No external source APIs, web search, live connector calls, model calls, deployments, downloads, uploads, installer actions, telemetry, or index/cache/ledger/candidate/master-index mutations were introduced by P82.

## P82 Identity Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/validate_identity_resolution_assessment.py --all-examples` | passed | 5 assessment examples validated. |
| `python scripts/validate_identity_resolution_assessment.py --all-examples --json` | passed | JSON parsed; `status=valid`, `errors=[]`. |
| `python scripts/validate_identity_cluster.py --all-examples` | passed | 5 cluster examples validated. |
| `python scripts/validate_identity_cluster.py --all-examples --json` | passed | JSON parsed; `status=valid`, `errors=[]`. |
| `python scripts/validate_cross_source_identity_resolution_contract.py` | passed | Contract validator reported `status=valid`. |
| `python scripts/validate_cross_source_identity_resolution_contract.py --json` | passed | JSON parsed; assessment examples 5, cluster examples 5. |
| `python scripts/dry_run_identity_resolution_assessment.py --left-label "Example App 1.0" --right-label "ExampleApp v1.0" --relation-type possible_same_object --json` | passed | Stdout-only dry run; no runtime, merge, live source call, or mutation flags enabled. |

## Page And Prior Contract Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/validate_comparison_page.py --all-examples` | passed | 5 comparison page examples. |
| `python scripts/validate_comparison_page_contract.py` | passed | P81 contract-only boundary intact. |
| `python scripts/validate_source_page.py --all-examples` | passed | 4 source page examples. |
| `python scripts/validate_source_page_contract.py` | passed | P80 contract-only boundary intact. |
| `python scripts/validate_object_page.py --all-examples` | passed | 4 object page examples. |
| `python scripts/validate_object_page_contract.py` | passed | P79 contract-only boundary intact. |
| `python scripts/run_external_baseline_comparison.py --batch batch_0 --json` | passed | No observations; comparison not eligible; 39 pending in Batch 0. |
| `python scripts/validate_external_baseline_comparison_report.py` | passed | P78 report valid; `eligibility=no_observations`. |
| `python scripts/verify_public_hosted_deployment.py --from-repo-config --json` | passed | Evidence command ran; static route evidence incomplete, backend URL not configured, deployment remains operator-gated. |
| `python scripts/validate_public_hosted_deployment_evidence.py` | passed | P77 report valid; static status `verified_failed`, backend `not_configured`. |

## Connector, Query, Safety, Static, And Eval Commands

All present connector approval validators passed for Software Heritage, npm, PyPI, GitHub Releases, Wayback/CDX/Memento, and Internet Archive metadata examples. Source cache/evidence ledger, source sync worker, query observation, shared query cache, search miss ledger, search need record, probe queue, candidate index, candidate promotion, known absence page, query privacy/poisoning guard, and demand dashboard validators passed.

Hosted local rehearsal passed with 60/60 checks, 9 safe routes, 5 safe queries, and 34/34 blocked requests. Public search safety evidence passed with 64/64 checks and 32/32 blocked requests. Static/search validation passed for the public search index builder, public index, hosted wrapper, static search integration, production contract, static deployment evidence, P50/P49 audit validators, public search API/result-card/safety/local-runtime checks, public search smoke in text and JSON modes, public index check, static site build check, static validation, publication inventory, public static site, GitHub Pages artifact check, generated artifact drift guard, and public alpha smoke.

Archive resolution evals passed with 6/6 satisfied tasks. Search usefulness audit passed with 64 queries; current public search remains `local_index_only` and still reflects fixture/source/capability/ranking/identity/external-baseline gaps.

## Unit And Boundary Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python -m unittest discover -s tests/scripts -t .` | passed | 540 tests. |
| `python -m unittest discover -s tests/operations -t .` | passed | 545 tests. |
| `python -m unittest discover -s tests/hardening -t .` | passed | 53 tests. |
| `python -m unittest discover -s tests/parity -t .` | passed | 25 tests. |
| `python -m unittest discover -s runtime -t .` | passed | 320 tests. |
| `python -m unittest discover -s surfaces -t .` | passed | 168 tests. |
| `python -m unittest discover -s tests -t .` | passed | 1254 tests. |
| `python scripts/check_architecture_boundaries.py` | passed | 446 Python files checked; no boundary violations. |
| `git diff --check` | passed | Exit code 0; Windows CRLF replacement warnings were emitted for existing static generated files. |

## Optional Commands

| Command | Result | Notes |
| --- | --- | --- |
| `cargo --version` | unavailable | `cargo` is not installed or not on PATH in this environment. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | `cargo` unavailable. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | `cargo` unavailable. |

GitHub Actions status was not checked because P82 forbids GitHub API calls and this milestone does not require Actions evidence.
