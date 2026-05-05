# Command Results

P86 focused validation:

- `python scripts/validate_public_query_observation_runtime_plan.py`: passed.
- `python scripts/validate_public_query_observation_runtime_plan.py --json`: passed; readiness decision `blocked_hosted_deployment_unverified`.
- `python -m unittest tests.operations.test_public_query_observation_runtime_plan tests.scripts.test_validate_public_query_observation_runtime_plan`: passed; 6 tests.

Hosted deployment gate:

- `python scripts/verify_public_hosted_deployment.py --from-repo-config --json`: completed without deployment/provider mutation; hosted backend URL is not configured, configured static URL verification remains failed/404, `deployment_verified=false`, and rate-limit evidence remains operator-gated.
- `python scripts/validate_public_hosted_deployment_evidence.py`: passed with warnings preserving the hosted-deployment gate.

Query-intelligence contracts:

- Query observation, query privacy/poisoning guard, shared query/result cache, search miss ledger, search need record, demand dashboard, and source sync worker validators passed as contract-only/deferred. No runtime observation, guard, cache, ledger, need, dashboard, source sync, or mutation behavior was added.

Public search/static/eval lanes:

- Public search contract, result-card contract, safety, local runtime, smoke, smoke JSON, safety evidence, hosted local rehearsal, static site, publication inventory, GitHub Pages artifact, and generated drift checks passed.
- Archive resolution evals passed 6/6 local-index tasks.
- Search usefulness audit passed for 64 queries: capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2; top gaps remain source coverage and compatibility evidence.
- External baseline report remains valid but ineligible for comparison: batch 0 has 0 observed and 39 pending manual observations; global slots are 0 observed and 192 pending.

Unit and boundary lanes:

- `python -m unittest discover -s tests/scripts -t .`: passed; 589 tests.
- `python -m unittest discover -s tests/operations -t .`: passed; 556 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed; 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed; 25 tests.
- `python -m unittest discover -s runtime -t .`: passed; 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed; 168 tests.
- `python -m unittest discover -s tests -t .`: passed; 1314 tests.
- `python scripts/check_architecture_boundaries.py`: passed; 446 Python files checked.
- `git diff --check`: passed with CRLF warnings only.

Optional:

- `gh --version`: unavailable; GitHub Actions status not checked.
- `cargo --version`: unavailable; optional Rust checks not run.
