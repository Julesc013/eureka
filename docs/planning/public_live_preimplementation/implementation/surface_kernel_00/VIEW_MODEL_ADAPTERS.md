# View Model Adapters

Implemented adapter entry point:

```text
runtime/surface/view_models.py
adapt_surface_view_model(route_id, payload)
```

Supported initial view families:

```text
resolution_run
public_search
workbench_run_review
candidate
need
generic route payloads
```

## Resolution Run

Adapts `ResolutionRunRecord` or the equivalent public envelope entry shape.

Projects:

```text
run id/kind/requested value/status
checked source ids/families
result_summary
absence_report
fallback_summary
```

Fallback summary is normalized so candidates and needs keep non-verified state.

## Workbench Run Review

Adapts output from:

```text
runtime/local/service/workbench_run_review_projection.py
```

Private posture can keep operator actions. Public posture receives a degraded safe projection because `workbench_run_review` is not a public route.

## Public Search

Adapts existing public-search response shape as an already-built public-safe payload. This task does not change public-search runtime behavior.
