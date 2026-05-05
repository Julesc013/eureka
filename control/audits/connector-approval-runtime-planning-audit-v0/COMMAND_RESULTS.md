# Command Results

Initial inspection:

- `git status --short --branch`: clean on `main...origin/main`.
- `git rev-parse HEAD`: `8c1d690119e267334ed3c7a2d59827dbddcbd672`.
- `git rev-parse origin/main`: `8c1d690119e267334ed3c7a2d59827dbddcbd672`.
- `git log --oneline -n 100`: P100 public search runtime integration audit
  commits are at the tip.

Evidence inspected:

- P71-P76 connector approval packs under `control/audits/`.
- P87-P92 connector runtime planning packs under `control/audits/`.
- Connector contracts under `contracts/connectors/`.
- Connector inventories under `control/inventory/connectors/`.
- Source sync, source cache, and evidence ledger contracts.
- P98/P99 local dry-run inventories.
- P100 public search runtime integration audit inventory.
- `runtime/connectors/` fixture/recorded adapters and public search runtime
  boundaries.

Final verification:

- `python scripts/validate_connector_approval_runtime_planning_audit.py`: passed.
- `python scripts/validate_connector_approval_runtime_planning_audit.py --json`: passed.
- `python scripts/report_connector_approval_runtime_status.py --json`: passed.
- `python scripts/validate_public_search_runtime_integration_audit.py`: passed.
- P99 evidence-ledger dry-run and validator: passed with 7 valid synthetic
  candidates and 0 invalid.
- P98 source-cache dry-run and validator: passed with 5 valid synthetic
  candidates and 0 invalid.
- Six first-wave connector runtime planning validators: passed.
- Six first-wave connector approval validators with `--all-examples`: passed,
  one synthetic example per connector.
- Source sync, source-cache/evidence-ledger, source cache, and evidence ledger
  contract validators: passed.
- External baseline comparison runner/validator: passed with 0 observed manual
  baseline records and 39 pending `batch_0` slots; comparison remains ineligible.
- Hosted deployment verifier/evidence validator: passed as evidence collection;
  backend URL is not configured and hosted checks remain operator-gated.
- Public search contract, result-card contract, safety, local runtime, and smoke
  commands: passed.
- Archive resolution evals: passed, 6 of 6 tasks satisfied.
- Search usefulness audit: passed, 64 queries; 5 covered, 40 partial, 10
  source gaps, 7 capability gaps, 2 unknown.
- External baseline status reporter: passed; manual observations remain pending.
- `python -m unittest discover -s tests/runtime -t .`: passed, 14 tests.
- `python -m unittest discover -s tests/scripts -t .`: passed, 663 tests.
- `python -m unittest discover -s tests/operations -t .`: passed, 618 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed, 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed, 25 tests.
- `python -m unittest discover -s runtime -t .`: passed, 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed, 168 tests.
- `python -m unittest discover -s tests -t .`: passed, 1464 tests.
- `python scripts/check_architecture_boundaries.py`: passed, 458 Python files
  checked.
- `git diff --check`: passed.

Optional local tools:

- `gh --version`: unavailable; `gh` is not installed in this shell.
- `gh auth status`: unavailable; `gh` is not installed in this shell.
- `cargo --version`: unavailable; `cargo` is not installed in this shell.
- Cargo workspace check/test: unavailable because `cargo` is not installed.
