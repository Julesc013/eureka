# Public Surface Audit

## Result

Public fallback projection remains read-only.

## Checks Added

`runtime/gateway/tests/test_resolution_runs_boundary.py` now checks the full public-disallowed operator action vocabulary against the public fallback summary and public run envelope.

The audit helper is:

```text
runtime/local/service/workbench_run_review_projection.py
public_surface_operator_action_audit(...)
```

## Findings

No new public route was added.

The public resolution run API still consumes run service output and projects the run envelope. It does not call fallback providers directly.

The public fallback summary still exposes only:

```text
view
inspect_evidence
```

It does not expose:

```text
review_candidate
promote
reject
supersede
mark_need
mark_near_miss
mark_policy_blocked
request_more_evidence
rebuild_index
```

## Auth Boundary Note

No new authenticated Workbench HTTP route was created in this task. The new projection module is a private runtime helper. A future route must enforce operator authorization before exposing its operator actions.
