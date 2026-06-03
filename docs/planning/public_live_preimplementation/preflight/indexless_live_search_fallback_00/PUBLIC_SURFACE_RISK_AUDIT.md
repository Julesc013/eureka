# Public Surface Risk Audit

## Public Paths Inspected

- `runtime/gateway/public_api/public_search.py`
- `runtime/gateway/public_api/public_alpha_readonly.py`
- `runtime/gateway/public_api/public_search_index.py`
- `runtime/gateway/public_api/search_boundary.py`
- `runtime/public_search/ux_mvp.py`
- `surfaces/web/workbench/render_public_search.py`
- `surfaces/web/server/workbench_server.py`
- `tests/hardening/test_public_search_safety_runtime.py`
- `runtime/gateway/tests/test_public_search_api.py`

## Risks

| Risk | Finding | Severity | Required handling |
| --- | --- | --- | --- |
| UI direct source calls | No browser/client direct source calls found, but `public_search.py` can call an Archive.org provider when configured. | high | Do not expand this hook as the main fallback path. Engine run service must own fallback source calls. |
| Unlabeled candidate display | Candidate cards are labeled candidate/review-required in public search and UX MVP. | medium | New fallback candidate cards must preserve labels. |
| Verified/candidate confusion | Public UX distinguishes candidates from verified/reviewed states. | medium | Tests must assert fallback candidate is not verified. |
| Operator-only action leakage | Public search blocks download/install/execute/upload/promote; review action is future-gated. | medium | Tests must assert review/promote/reject/rebuild_index absent or blocked in public output. |
| Public fallback fanout | Public search status says live probes disabled but optional metadata candidate search can perform an external call. | high | Public route must call engine run/projection only, or keep source-policy opt-in behind engine. |
| Source details exposed beyond policy | Public candidate details include Archive.org detail URLs and metadata summaries. | medium | Keep public-safe redaction and no raw response commit. |
| Private local data exposure | Hardening tests check private path sentinels; public alpha forbids local path params. | low | Preserve redaction and forbidden param behavior. |
| Legacy/client compatibility risk | Public search schema has stable/experimental/future fields; adding fallback fields may affect clients. | medium | Add backward-compatible fields and keep existing result path unchanged. |

## Current Surface Safety Strengths

- Public alpha read-only API rejects live/source/download/install/upload/local
  path/credential controls.
- Public search validates query length, allowed params, forbidden params, source
  policy values, and unsafe modes.
- Public result actions block downloads, installs, execution, uploads, accepts,
  and promotion.
- UX MVP has policy assertions for no public mutation and no live source fanout.

## Required Public Tests For Fallback

- Public query without fallback remains local-index-only unless policy enables
  fallback.
- Public route does not instantiate or call source provider directly.
- Public fallback candidate is labeled candidate/review-required.
- Public fallback response blocks operator actions.
- Public fallback response does not expose local/private paths, raw response
  payloads, credentials, or unsafe source controls.
