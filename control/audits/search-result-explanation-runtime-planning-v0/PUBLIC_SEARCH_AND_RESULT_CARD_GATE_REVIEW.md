# Public Search And Result-Card Gate Review

Status: local public-search foundation present; hosted/operator gate remains.

Public search API contract:

- `contracts/api/search_request.v0.json`
- `contracts/api/search_response.v0.json`
- `docs/reference/PUBLIC_SEARCH_API_CONTRACT.md`

Result-card contract:

- `contracts/api/search_result_card.v0.json`
- `docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`

Runtime:

- `runtime/gateway/public_api/public_search.py` implements local `local_index_only`
  public search.
- `runtime/gateway/public_api/public_search_index.py` loads the controlled public
  index artifacts.

Current route status:

- Local routes exist for search/status/source endpoints.
- No `/api/v1/result/{result_id}/explanation` route exists.
- No explanation route is added by P106.

Current response format includes public result cards, checked sources, gaps,
warnings, generated_by, and stability fields. Result cards expose enough public
fields for a future explanation assembler to reference match, source, evidence,
compatibility, action, warning, limitation, and gap components, but that future
assembler remains disabled.

Blocked-parameter safety is covered by the public search safety validators and
P100 safety audit. Public request parameters must not select explanation,
ranking, index, cache, ledger, candidate, source root, URL, model, local path,
or filesystem roots.

