# Route Implementation Status

| Route | P54 status | Notes |
| --- | --- | --- |
| `GET /healthz` | implemented_local_prototype | Public-safe health document only. |
| `GET /status` | implemented_local_prototype | Public status with deployment-unverified flags. |
| `GET /search?q=...` | implemented_local_prototype | Server-rendered no-JS HTML. |
| `GET /api/v1/status` | implemented_local_prototype | JSON status envelope. |
| `GET /api/v1/search?q=...` | implemented_local_prototype | JSON search response from existing public API. |
| `GET /api/v1/query-plan?q=...` | implemented_local_prototype | Deterministic local query plan. |
| `GET /api/v1/sources` | implemented_local_prototype | Public-safe source summaries. |
| `GET /api/v1/source/{source_id}` | implemented_local_prototype | Public-safe source detail. |
| `GET /api/v1/object/{id}` | contract_only | Deferred. |
| `GET /api/v1/result/{id}` | contract_only | Deferred. |
| `GET /api/v1/absence/{need_id}` | contract_only | Deferred. |
| `GET /api/v1/capabilities` | contract_only | Deferred. |

All implemented routes remain local rehearsal routes until an operator records
hosted deployment evidence.
