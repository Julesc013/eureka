# Route Contract

| Route | Method | Classification | Notes |
|---|---|---:|---|
| `/healthz` | GET | hosted_future | P54 liveness endpoint. |
| `/status` | GET | hosted_future | P54 human/public status endpoint. |
| `/search?q=...` | GET | implemented_local_prototype | Local HTML route exists; hosted route is future. |
| `/api/v1/status` | GET | implemented_local_prototype | Local JSON status exists; hosted route is future. |
| `/api/v1/search?q=...` | GET | implemented_local_prototype | Local JSON search exists in `local_index_only`. |
| `/api/v1/query-plan?q=...` | GET | implemented_local_prototype | Local deterministic planner route exists. |
| `/api/v1/sources` | GET | implemented_local_prototype | Local public-safe source summary route exists. |
| `/api/v1/source/{source_id}` | GET | implemented_local_prototype | Local public-safe source detail route exists. |
| `/search.html` | GET | static_handoff | Static no-JS handoff, not hosted search. |
| `/api/v1/object/{id}` | GET | contract_only | Future object detail. |
| `/api/v1/result/{id}` | GET | contract_only | Future result detail. |
| `/api/v1/absence/{need_id}` | GET | contract_only | Future absence report. |
| `/api/v1/compare` | GET | deferred | Future comparison. |
| `/api/v1/capabilities` | GET | contract_only | Future capability flags. |

V0 route defaults: GET-only, no POST body, no uploads, no arbitrary URL fetch,
no downloads or install actions, no accounts, no caller-provided local paths,
and no live source fanout.
