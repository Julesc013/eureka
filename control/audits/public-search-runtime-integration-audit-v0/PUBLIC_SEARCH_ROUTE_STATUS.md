# Public Search Route Status

Implemented local/prototype routes:

| Route | Classification | Current behavior |
| --- | --- | --- |
| `/search` | `implemented_local_runtime` | Local HTML search over `local_index_only` records. |
| `/api/v1/search` | `implemented_local_runtime` | JSON search over controlled local/public index records. |
| `/api/v1/query-plan` | `implemented_local_runtime` | Deterministic query-plan projection for bounded local queries. |
| `/api/v1/status` | `implemented_local_runtime` | Capability/status flags with unsafe capabilities disabled. |
| `/api/v1/sources` | `implemented_local_runtime` | Public-safe source summaries. |
| `/api/v1/source/{source_id}` | `implemented_local_runtime` | Public-safe source detail for governed source IDs. |

Future or absent routes:

| Route | Classification | Notes |
| --- | --- | --- |
| `/object/{object_id}` | `absent` | No public route currently implemented. |
| `/source/{source_id}` | `absent` | Public API has `/api/v1/source/{source_id}` only. |
| `/comparison/{comparison_id}` | `absent` | Comparison runtime is planning-only. |
| `/api/v1/object/{object_id}` | `planning_only` | Reserved/future only. |
| `/api/v1/source-page/{source_id}` | `absent` | Source page runtime is planning-only. |
| `/api/v1/comparison/{comparison_id}` | `planning_only` | Reserved/future only. |
| `/api/v1/result/{result_id}/explanation` | `absent` | Explanation contract is contract-only. |
| `/api/v1/result-group/{group_id}/explanation` | `absent` | Explanation runtime is absent. |

No route changes were made by P100.

