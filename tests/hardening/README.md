# Hard Test Pack v0

Hard Test Pack v0 is Eureka's first dedicated regression-guard lane for risks found by the Comprehensive Test/Eval Operating Layer and Repo Audit v0.

These tests protect against silent degradation in areas where ordinary unit tests are too narrow:

- hard eval weakening
- fabricated external baselines
- public-alpha local path leakage
- route inventory drift
- README command drift
- documentation link drift
- Python oracle golden drift
- Rust parity structure drift
- source placeholder dishonesty
- resolution-memory privacy/path leakage
- AIDE/test registry inconsistency

## What This Pack Does

- Uses `unittest` and stdlib helpers only.
- Checks repo artifacts, docs, scripts, eval outputs, and public-alpha policy behavior.
- Runs bounded local commands with timeouts where the command is meant to be safe and short.
- Treats Cargo checks as optional; Python tests do not require a Rust toolchain.
- Keeps external baselines manual/pending unless committed observation evidence exists.

## What This Pack Does Not Do

- It does not implement product behavior.
- It does not add retrieval, ranking, fuzzy, vector, LLM, crawling, or connector behavior.
- It does not prove production readiness.
- It does not perform live Google, Internet Archive, or web searches.
- It does not replace the broader runtime, surface, eval, or architecture test lanes.

## How To Run

```bash
python -m unittest discover -s tests/hardening -t .
```

The hardening lane is also represented in `control/inventory/tests/command_matrix.json` and is intended to be run before syncing repo-wide governance, eval, public-alpha, parity, or documentation changes.

## Adding Future Hard Tests

Add a focused `test_*.py` file under this directory when an audit identifies a failure mode that should never silently recur. Prefer checks that:

- validate a concrete artifact or command,
- avoid environment-specific assumptions,
- explain the risk in the test name,
- fail with actionable messages,
- preserve honest capability gaps instead of making tests green by weakening fixtures.
