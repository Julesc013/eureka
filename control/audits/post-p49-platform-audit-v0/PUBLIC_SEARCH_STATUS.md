# Public Search Status

| Area | Evidence | Classification | Notes |
|---|---|---|---|
| Public search API contract | `validate_public_search_contract.py` | `contract_only` | Request, response, error, and route envelopes are governed. |
| Result-card contract | `validate_public_search_result_card_contract.py` | `contract_only` | Cards include action/risk/rights guard fields. |
| Safety and abuse guard | `validate_public_search_safety.py` | `contract_only` | `local_index_only` is the only v0 mode. |
| Local runtime routes | `validate_local_public_search_runtime.py` | `implemented_local_prototype` | `/search`, `/api/v1/search`, `/api/v1/query-plan`, `/api/v1/status`, `/api/v1/sources`, `/api/v1/source/{source_id}`. |
| Smoke evidence | `public_search_smoke.py --json` | `implemented_local_prototype` | 30 checks passed, including blocked unsafe requests. |
| Static handoff | `validate_public_search_static_handoff.py` | `implemented_static_artifact` | Static/no-JS handoff exists; hosted backend status is unavailable. |
| Rehearsal | `validate_public_search_rehearsal.py` | `implemented_local_prototype` | 9 safe queries and 14 blocked requests passed. |
| Hosted public search | no deployed backend evidence | `operator_gated` | No hosted URL, provider config, production API, or deployment evidence. |

Blocked behavior evidence includes arbitrary URL fetches, caller-provided local
paths, credentials, downloads, installs, uploads, live-source parameters, and
live probe modes.
