# Contract Alignment Review

The rehearsal aligns with the governed public search contracts:

- Request validation follows `contracts/api/search_request.v0.json` for required
  `q`, query length, limit bounds, supported profiles/includes, and
  `local_index_only` mode.
- Success responses follow `contracts/api/search_response.v0.json` with
  `ok: true`, mode, query, limits, results, checked sources, gaps, warnings,
  generated-by metadata, and stability fields.
- Result cards follow `contracts/api/search_result_card.v0.json` for result id,
  title, record kind, lane, user cost, source, identity, evidence,
  compatibility, actions, warnings, and limitations.
- Error responses follow `contracts/api/error_response.v0.json` for governed
  error codes such as `query_required`, `query_too_long`,
  `limit_too_large`, `local_paths_forbidden`, `downloads_disabled`,
  `installs_disabled`, `uploads_disabled`, and `live_probes_disabled`.
- `control/inventory/publication/public_search_safety.json` remains the safety
  source for forbidden parameters, disabled modes, request/result limits, and
  privacy defaults.

Known contract posture:

- Search is local/prototype runtime only.
- Hosted public search is not configured.
- Live backend and live probe contracts remain disabled/future.
- No production API guarantee, malware-safety claim, rights-clearance claim,
  executable download surface, or installer handoff is added.
