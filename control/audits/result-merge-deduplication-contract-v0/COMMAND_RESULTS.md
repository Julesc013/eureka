# Command Results

Verification was run locally from `d:\Projects\Eureka\eureka` on 2026-05-05. P83 performed no external source API calls, web browsing, search-engine calls, live connector calls, model calls, deployments, downloads, uploads, installer actions, telemetry, runtime result grouping, deduplication, result suppression, ranking changes, or index/cache/ledger/candidate/master-index mutations.

## P83 Result Merge Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/validate_result_merge_group.py --all-examples` | passed | 5 result merge group examples validated. |
| `python scripts/validate_result_merge_group.py --all-examples --json` | passed | JSON parsed; `status=valid`, `errors=[]`. |
| `python scripts/validate_deduplication_assessment.py --all-examples` | passed | 5 deduplication assessment examples validated. |
| `python scripts/validate_deduplication_assessment.py --all-examples --json` | passed | JSON parsed; `status=valid`, `errors=[]`. |
| `python scripts/validate_result_merge_deduplication_contract.py` | passed | Contract validator reported `status=valid`. |
| `python scripts/validate_result_merge_deduplication_contract.py --json` | passed | JSON parsed; group examples 5, assessment examples 5. |
| `python scripts/dry_run_result_merge_group.py --left-title "Example App 1.0" --right-title "ExampleApp v1.0" --relation-type near_duplicate_result --json` | passed | Stdout-only dry run; no runtime grouping, merge, ranking change, live source call, or mutation flags enabled. |

## Prior Contract And Evidence Commands

P82 identity assessment, cluster, and contract validators passed. P81 comparison page, P80 source page, and P79 object page validators passed. P78 external baseline comparison remained valid but not eligible: Batch 0 has 0 observed and 39 pending records. P77 hosted evidence remains valid but operator-gated: static site status `verified_failed`, hosted backend status `not_configured`.

## Connector, Query, Safety, Static, And Eval Commands

All present connector approval validators passed for Software Heritage, npm, PyPI, GitHub Releases, Wayback/CDX/Memento, and Internet Archive metadata examples. Source cache/evidence ledger, source sync worker, query observation, shared query cache, search miss ledger, search need record, probe queue, candidate index, candidate promotion, known absence page, query privacy/poisoning guard, and demand dashboard validators passed.

Hosted local rehearsal passed with 60/60 checks, 9 safe routes, 5 safe queries, and 34/34 blocked requests. Public search safety evidence passed with 64/64 checks and 32/32 blocked requests. Static/search validation passed for static search integration, public index builder, public index, hosted wrapper, hosted wrapper check/config, production contract, static deployment evidence, P50/P49 audit validators, public search API/result-card/safety/local-runtime checks, public search smoke text/JSON, public index check, static site build check, static validation, publication inventory, public static site, GitHub Pages artifact check, generated artifact drift guard, and public alpha smoke.

Archive resolution evals passed with 6/6 satisfied tasks. Search usefulness audit passed with 64 queries and status counts: `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`.

## Unit And Boundary Commands

| Command | Result | Notes |
| --- | --- | --- |
| `python -m unittest discover -s tests/scripts -t .` | passed | 555 tests. |
| `python -m unittest discover -s tests/operations -t .` | passed | 548 tests. |
| `python -m unittest discover -s tests/hardening -t .` | passed | 53 tests. |
| `python -m unittest discover -s tests/parity -t .` | passed | 25 tests. |
| `python -m unittest discover -s runtime -t .` | passed | 320 tests. |
| `python -m unittest discover -s surfaces -t .` | passed | 168 tests. |
| `python -m unittest discover -s tests -t .` | passed | 1272 tests. |
| `python scripts/check_architecture_boundaries.py` | passed | 446 Python files checked; no boundary violations. |
| `git diff --check` | passed | Exit code 0; Windows CRLF replacement warnings were emitted for existing static generated files. |
| `git status --short --branch` | passed | Worktree had expected P83 changes before commit. |

## Optional Commands

| Command | Result | Notes |
| --- | --- | --- |
| `cargo --version` | unavailable | `cargo` is not installed or not on PATH in this environment. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | `cargo` unavailable. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | `cargo` unavailable. |

GitHub Actions status was not checked because P83 forbids GitHub API calls and this milestone does not require Actions evidence.
