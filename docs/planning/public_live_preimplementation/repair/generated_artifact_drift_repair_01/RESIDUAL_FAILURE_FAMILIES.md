# Residual Failure Families

| Family | Status | Notes |
|---|---|---|
| `generated_artifact_drift` | repaired / not reproducible as real artifact drift | Current generated-artifact validators pass; summary parser false positive repaired. |
| `contract_schema_drift` | still blocked | Not repaired by this task. |

## Gates

| Gate | Status |
|---|---|
| public alpha | blocked |
| `dev -> main` | blocked |
| source/snapshot release gate | blocked pending external full-discovery rerun |

Do not mark release readiness green until an external full-discovery rerun is
current to the repaired HEAD.

