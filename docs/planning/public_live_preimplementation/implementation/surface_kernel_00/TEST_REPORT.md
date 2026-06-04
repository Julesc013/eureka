# Test Report

Added focused tests:

```text
tests/runtime/test_surface_kernel.py
tests/runtime/test_surface_output_policy.py
tests/runtime/test_surface_capability_negotiation.py
tests/runtime/test_surface_cache_key.py
```

Coverage:

```text
public route projection filters operator-only actions
private Workbench route can expose operator actions only in private posture
fallback candidate projects as candidate, never verified
fallback need projects as need
policy_blocked remains policy_blocked
unavailable remains unavailable
unknown status degrades to unknown
unknown action is hidden from public policy output
profile negotiation honors explicit safe profile
profile negotiation falls back to safe default
cache key changes by required dimensions
renderer dispatch receives policy-filtered view model
renderer dispatch does not call source providers
SurfaceKernel does not mutate reviewed/public/master indexes
```

Focused local command:

```text
py -3 -m unittest tests.runtime.test_surface_kernel tests.runtime.test_surface_output_policy tests.runtime.test_surface_capability_negotiation tests.runtime.test_surface_cache_key tests.runtime.test_workbench_run_review_projection runtime.gateway.tests.test_resolution_runs_boundary runtime.gateway.tests.test_resolution_runs_view_models runtime.gateway.tests.test_public_search_api
```

Observed result before final validation report:

```text
Ran 30 tests
OK
```
