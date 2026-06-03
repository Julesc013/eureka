# Test Report

## Focused Tests Added

`tests/runtime/test_review_ledger.py`

Coverage:

- fallback candidate handoff remains non-promoted
- boundary report blocks candidate/fallback/source self-promotion
- promote requires review item, citation, and local-only confirmation
- promote records decision and audit event
- reject preserves audit reason and rejected status
- request-more-evidence keeps item out of reviewed projection
- decision requires citation or rationale

## Initial Focused Test Results

```text
py -3 -m unittest tests.runtime.test_review_ledger
```

Result:

```text
Ran 6 tests
OK
```

```text
py -3 -m unittest tests.runtime.test_review_queue_store
```

Result:

```text
Ran 18 tests
OK
```

```text
py -3 -m unittest runtime.gateway.tests.test_resolution_runs_boundary runtime.gateway.tests.test_resolution_runs_view_models
```

Result:

```text
Ran 8 tests
OK
```

Final focused validation is recorded in `VALIDATION_REPORT.md`.
