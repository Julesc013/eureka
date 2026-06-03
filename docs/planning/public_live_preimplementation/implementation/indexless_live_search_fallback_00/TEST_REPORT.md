# Test Report

## Focused Tests Added Or Updated

- `runtime/engine/resolution_runs/tests/test_service.py`
  - local reviewed result path unchanged
  - fallback provider is not called when local results exist
  - local miss records fallback candidate when policy allows
  - local lookup unavailable can record fallback candidate
  - fallback disabled blocks without provider call
  - source family disabled blocks without provider call
  - source allowlist denial blocks without provider call
  - budget exceeded degrades without provider call
  - source timeout degrades without truth promotion
  - zero-candidate fallback records a need
- `runtime/engine/resolution_runs/tests/test_run_store.py`
  - fallback summary persists and reloads
- `runtime/gateway/tests/test_resolution_runs_boundary.py`
  - fallback summary projects without operator actions
- `runtime/gateway/tests/test_resolution_runs_view_models.py`
  - fallback summary maps through the shared view model

## Focused Test Command

```text
py -3 -m unittest runtime.engine.resolution_runs.tests.test_service runtime.engine.resolution_runs.tests.test_run_store runtime.gateway.tests.test_resolution_runs_boundary runtime.gateway.tests.test_resolution_runs_view_models runtime.gateway.tests.test_public_search_api
```

Result:

```text
Ran 29 tests in 0.465s
OK
```

## Full Discovery

Full unittest discovery was not run inside the AI session, per repo policy. The changed-test selector did not require external full discovery.
