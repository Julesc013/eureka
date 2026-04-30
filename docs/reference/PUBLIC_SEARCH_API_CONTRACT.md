# Public Search API Contract v0

Status: implemented as a contract only.

Public Search API Contract v0 reserves the first public search request,
response, error, and route shapes before any hosted public search runtime exists.
It does not make `/search` or `/api/v1/search` live, does not deploy a backend,
and does not claim production API stability.

## Contract Files

- Request schema: `contracts/api/search_request.v0.json`
- Response schema: `contracts/api/search_response.v0.json`
- Error schema: `contracts/api/error_response.v0.json`
- Result-card schema: `contracts/api/search_result_card.v0.json`
- Route inventory: `control/inventory/publication/public_search_routes.json`
- Local-index-only mode: `docs/operations/PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md`
- Safety guard: `docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`
- Runtime readiness checklist:
  `docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`

The first allowed mode is `local_index_only`. Future public search must accept a
bounded user query, search a controlled local index, and return result lanes,
user-cost hints, compatibility summaries, source/evidence summaries, and bounded
absence information. It must not fan out to live Internet Archive, Google,
package registries, arbitrary URLs, user local paths, uploads, downloads, or
installers.

## Request

The v0 request is GET-compatible and has an equivalent JSON-body shape reserved
for a future POST review. The required field is:

- `q`: string, required, maximum 160 characters, rejected when empty after
  trimming.

Optional fields:

- `limit`: integer, default 10, minimum 1, maximum 25.
- `offset`: experimental integer offset, default 0.
- `cursor`: future pagination token, not required by v0.
- `profile`: one of `standard_web`, `lite_html`, `text`, or `api_client`.
- `mode`: `local_index_only` only.
- `include`: optional summary expansions: `query_plan`, `source_summaries`,
  `evidence_summaries`, `compatibility_summaries`, `absence_summary`.
- `source_policy`: `local_index_only` only.

Forbidden parameters include `index_path`, `store_root`, `run_store_root`,
`task_store_root`, `memory_store_root`, `local_path`, `path`, `file_path`,
`directory`, `root`, `url`, `fetch_url`, `crawl_url`, `source_url`, `download`,
`install`, `execute`, `upload`, `user_file`, `live_probe`, `live_source`,
`network`, `arbitrary_source`, `source_credentials`, `auth_token`, and
`api_key`.

## Response

Successful responses use `ok: true`, `schema_version: 0.1.0`,
`contract_id: eureka_public_search_response_v0`, and `mode:
local_index_only`.

The envelope includes:

- `query`: raw and normalized query text, interpreted task kind if available,
  and notices.
- `limits`: result and query length limits.
- `results`: compact result-card records.
- `checked_sources`: sources considered as local index, recorded fixture,
  static summary, or not checked.
- `gaps`: bounded coverage gaps and possible next actions.
- `warnings`: non-fatal warnings.
- `absence_summary`: optional bounded absence explanation.
- `generated_by`: future implementation provenance.
- `stability`: field-level stability categories.
- `links` and `debug`: optional fields; `debug` is future/disabled by default.

The v0 result shape is governed by Public Search Result Card Contract v0 in
`contracts/api/search_result_card.v0.json` and
`docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`. Compact P26 aliases
remain in `search_response.v0.json` for old clients: `result_id`, `title`,
optional `subtitle`, `record_kind`, `source_id`, `source_family`,
`public_target_ref`, optional `resolved_resource_id`, `result_lane`,
`user_cost`, `compatibility`, `evidence`, `actions`, `links`, and
`limitations`.

Result actions do not require or imply download URLs, install URLs, private local
paths, raw source payloads, executable trust claims, rights clearance, or malware
scan claims. Public Search Result Card Contract v0 refines display fields,
source/evidence/compatibility posture, action gating, rights caveats, and risk
caveats without enabling those behaviors.

## Errors

Errors use `ok: false`, `schema_version: 0.1.0`, `contract_id:
eureka_public_search_error_response_v0`, and an `error` object containing
`code`, `message`, `status`, and `retryable`. Optional fields include
`capability_required`, `parameter`, and `docs`.

Required v0 error codes are:

- `bad_request`
- `query_required`
- `query_too_long`
- `limit_too_large`
- `unsupported_mode`
- `unsupported_profile`
- `unsupported_include`
- `forbidden_parameter`
- `local_paths_forbidden`
- `downloads_disabled`
- `installs_disabled`
- `uploads_disabled`
- `live_probes_disabled`
- `live_backend_unavailable`
- `rate_limited`
- `timeout`
- `not_found`
- `internal_error`

These codes are contract definitions only. They do not add runtime error
handling.

## Reserved Routes

The route inventory reserves:

- `GET /search`: future hosted HTML search for `standard_web`, `lite_html`, and
  `text` profiles.
- `GET /api/v1/search`: future JSON search for `api_client`.
- `GET /api/v1/query-plan`: future deterministic query-plan endpoint.
- `GET /api/v1/status`: future backend status/capability endpoint.
- `GET /api/v1/sources`: future source summary endpoint.
- `GET /api/v1/source/{source_id}`: future source detail endpoint.

Every route is `future_contract`, requires a future backend, and has
`implemented_now: false`. Live probes, downloads, local paths, uploads, and
external source fanout are disabled for all routes.

## Client Degradation

`standard_web` may receive full HTML once a future runtime exists. `lite_html`
must receive simple no-JS HTML. `text` must receive plain-text output or a
static handoff page. `api_client` receives JSON only. Old clients should lose
interactive affordances first; they should not lose source labels, result lanes,
user-cost explanations, compatibility summaries, warnings, or absence notes.

## Related Contracts

The live backend handoff reserves `/api/v1` but keeps it future and not live.
This contract narrows the public search part of that reservation. The live probe
gateway remains disabled and does not become an implementation detail of
`local_index_only`. Public data summaries under `site/dist/data` remain static
publication artifacts, not a live search API. Native clients, relay consumers,
and snapshot consumers may reference this contract as future input, but no
native client, relay runtime, or snapshot reader runtime is implemented here.

## Versioning

Contract v0 is experimental with field-level stability labels. Stable-draft
fields should not be removed or renamed without an explicit follow-up note.
Experimental and future fields may change before a stable public API exists.
New optional fields are non-breaking only when old clients can ignore them.

## Runtime Preconditions

Before any runtime route implements this contract, the repo needs Public Search
Safety / Abuse Guard v0, Local Public Search Runtime v0, rate-limit policy,
hosted backend handoff review, local-index ownership, public-alpha operator
signoff, and validation proving no live probes, downloads, uploads, local path
search, arbitrary URL fetch, account behavior, telemetry, or production claims
were added by accident. Public Search Result Card Contract v0 is now the
governed `results[]` card contract; it still does not make public search live.
Public Search Safety / Abuse Guard v0 is now implemented as policy/contract
only. It defines `local_index_only` as the only allowed v0 mode, bounded
request/result/time limits, forbidden URL/local-path/credential/action
parameters, disabled live/external modes, error mapping, privacy defaults, and
operator controls without implementing route handlers, rate-limit middleware,
telemetry runtime, live probes, downloads, uploads, arbitrary URL fetch, or
production safety claims. The next runtime milestone must satisfy its
inventory, validator, and runtime readiness checklist before adding route
behavior.

## Out Of Scope

This contract does not implement public search runtime, hosted backend
deployment, live source probes, Internet Archive calls, Google queries,
arbitrary URL fetch, crawling, downloads, installers, uploads, accounts,
telemetry, native clients, relay runtime, snapshot reader runtime, TLS, auth,
rate limiting, process management, custom domains, production API stability, or
production readiness.
