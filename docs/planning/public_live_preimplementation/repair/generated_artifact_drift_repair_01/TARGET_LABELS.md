# Target Labels

| Family | Reported label | Classification | Confidence | Notes |
|---|---|---|---|---|
| `unittest-cb1ded72f5fc441c` | `refusing forbidden output root: site/dist` | `validator_expectation_drift` / summary parser false positive | High | The reported label is expected validator output, not a unittest label. |

## External Evidence

The external `failed_tests.txt` listed:

`refusing forbidden output root: site/dist`

The external stdout showed many expected negative-path checks printing
`ERROR: refusing forbidden output root: ...` while their surrounding tests
continued and passed. The summary parser treated those plain diagnostic lines as
unittest failure headers.

## Current Repo Evidence

Current generated-artifact checks pass:

- `python scripts/validate_generated_artifact_drift.py --json`
- `python scripts/check_generated_artifact_drift.py --json`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_generated_artifact_drift tests.tools.test_audit_generated_artifact_visibility`

