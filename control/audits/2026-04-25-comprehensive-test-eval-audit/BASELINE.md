# Baseline

Audit name: Comprehensive Test/Eval Operating Layer and Repo Audit v0

Date: 2026-04-25

Purpose: create a durable test/eval/audit operating layer and use it to
summarize Eureka's current structure, coverage, behavior, test gaps, and next
milestone recommendations.

Current branch/status at baseline: `main...origin/main`, clean before this
audit started.

Current known maturity: Python reference backend prototype and temporal object
resolver, with bounded local deterministic seams, public-alpha constrained
mode, archive-resolution eval runner, search usefulness audit, Python oracle
goldens, and a first isolated Rust source-registry parity candidate.

Current accepted next milestone before this audit:
`Search Usefulness Backlog Triage v0`.

Current key verification commands:

- `python -m unittest discover -s runtime -t .`
- `python -m unittest discover -s surfaces -t .`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/public_alpha_smoke.py`
- `python scripts/generate_python_oracle_golden.py --check`
- `python scripts/run_archive_resolution_evals.py`
- `python scripts/run_search_usefulness_audit.py`
- `git diff --check`
- `git status --short --branch`

Explicit scope statement: this is an audit and governance task. It does not
implement new product behavior, does not add source connectors, does not add
live crawling or external scraping, does not add Rust behavior ports, does not
add native apps, and does not make production-readiness claims.

