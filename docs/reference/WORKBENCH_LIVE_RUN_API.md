# Workbench Live Run API

API envelope:

```json
{
  "schema_version": "workbench_live_run_api_response.v0",
  "request_id": "",
  "run_id": "",
  "projection_profile": "operator_workbench",
  "state": "completed",
  "data": {},
  "warnings": [],
  "limitations": [],
  "blocked_actions": []
}
```

The API exposes read-only run inspection over process-local dry-run packets. It does not persist operator instance state and does not create accepted evidence, reviewed records, or master/public truth.
