# Validation Matrix

```json
{
  "full_discovery": "NOT_RUN_BY_POLICY",
  "schema_version": "snapshot_refresh_03_validation_matrix.v0",
  "status": "pass_with_warnings",
  "warnings": [
    "AIDE verify advisory context-ref warnings only; 0 errors"
  ],
  "task": "SNAPSHOT-REFRESH-03",
  "validation_commands": [
    "python scripts/validate_snapshot_refresh.py",
    "python scripts/validate_local_apply_live_metadata_previews.py",
    "focused snapshot refresh unittest modules"
  ]
}
```
