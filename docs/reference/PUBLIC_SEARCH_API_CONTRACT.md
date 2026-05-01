# Public Search API Contract v0

Status: implemented as a contract-first local/prototype runtime boundary.

Public Search API Contract v0 reserves the first public search request,
response, error, and route shapes before any hosted public search runtime exists.
Local Public Search Runtime v0 now implements `/search`, `/api/v1/search`,
`/api/v1/query-plan`, `/api/v1/status`, `/api/v1/sources`, and
`/api/v1/source/{source_id}` through the local stdlib workbench server. This is
local/prototype backend runtime only. It does not make public search hosted,
does not deploy a backend, and does not claim production API stability. Public
Search Static Handoff v0 now publishes the no-JS static handoff page and
machine-readable handoff status under `site/dist`, but that handoff remains
static publication only.
This is not hosted public deployment.
It does not claim production API stability.
Public Search Safety / Abuse Guard v0 remains the safety source for these local
routes and any later hosted rehearsal.

Public Search Safety Evidence v0 records executable local evidence for this
contract: safe queries work, dangerous parameters are rejected, result/query
limits are enforced, status endpoints stay honest, and the static handoff plus
public index remain public-safe. This evidence is not hosted deployment proof.

## Contract Files

- Request schema: `contracts/api/search_request.v0.json`
- Response schema: `contracts/api/search_response.v0.json`
- Error schema: `contracts/api/error_response.v0.json`
- Result-card schema: `contracts/api/search_result_card.v0.json`
- Source-status schema: `contracts/api/source_status.v0.json`
- Evidence-summary schema: `contracts/api/evidence_summary.v0.json`
- Absence-report schema: `contracts/api/absence_report.v0.json`
- Public-search status schema: `contracts/api/public_search_status.v0.json`
- Production-facing contract summary:
  `docs/reference/PUBLIC_SEARCH_PRODUCTION_CONTRACT.md`
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
- `profile`: one of `standard_web`, `lite_html`, `text`, `api_client`,
  `snapshot`, or `native_client`.
- `mode`: `local_index_only` only.
- `include`: optional summary expansions: `query_plan`, `source_summaries`,
  `evidence_summaries`, `compatibility_summaries`, `absence_summary`,
  `evidence`, `compatibility`, `source_summary`, `limitations`, `gaps`, or
  `actions`.
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
- `result_count`, `checked`, `limitations`, `absence`, `source_status`,
  `timing`, `request_limits`, `next_actions`, and disabled capability flags are
  production-facing additive fields for the hosted wrapper contract.
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
- `arbitrary_url_fetch_forbidden`
- `downloads_disabled`
- `installs_disabled`
- `uploads_disabled`
- `live_probes_disabled`
- `live_backend_unavailable`
- `rate_limited`
- `timeout`
- `not_found`
- `internal_error_public_safe`
- `internal_error`

These codes are the governed vocabulary. Local Public Search Runtime v0 uses
the bounded request-validation errors for local/prototype routes; hosted runtime
must use the public-safe subset documented in
`docs/reference/PUBLIC_ERROR_CONTRACT.md`.

## Local Runtime Routes

The route inventory now records local/prototype runtime handlers for:

- `GET /search`: server-rendered no-JS HTML search for `standard_web`.
- `GET /api/v1/search`: governed JSON search for `api_client`.
- `GET /api/v1/query-plan`: deterministic public query-plan endpoint.
- `GET /api/v1/status`: public-search status/capability endpoint.
- `GET /api/v1/sources`: public-safe source summary endpoint.
- `GET /api/v1/source/{source_id}`: public-safe source detail endpoint.

Every route is marked `local_runtime_implemented`, `implementation_scope:
local_prototype_backend`, and `hosted_public_deployment: false`. Live probes,
downloads, local paths, uploads, and external source fanout are disabled for all
routes. Rate limiting remains required before any hosted public exposure.

## Client Degradation

`standard_web` receives no-JS local/prototype HTML from `/search`. `lite_html`
and `text` remain degradation profiles for later static handoff work and should
preserve source labels, result lanes, user-cost explanations, compatibility
summaries, warnings, and absence notes. `api_client` receives JSON only.

## Related Contracts

The live backend handoff still reserves hosted `/api/v1` behavior for future
deployment review. Local Public Search Runtime v0 is not hosted public
deployment and does not change GitHub Pages, which remains static-only. The
live probe gateway remains disabled and does not become an implementation
detail of `local_index_only`. Public data summaries under `site/dist/data`
remain static publication artifacts, not a live search API; this includes
`site/dist/data/search_handoff.json`, which records that hosted search is
unavailable/unverified. Native clients,
relay consumers, and snapshot consumers may reference this contract as input,
but no native client, relay runtime, or snapshot reader runtime is implemented
here.

## Versioning

Contract v0 is experimental with field-level stability labels. Stable-draft
fields should not be removed or renamed without an explicit follow-up note.
Experimental and future fields may change before a stable public API exists.
New optional fields are non-breaking only when old clients can ignore them.

## Runtime Preconditions

Local Public Search Runtime v0 satisfies the first local route implementation
gate. Hosted rehearsal still needs rate-limit policy, hosted backend handoff
review, operator controls, public-alpha signoff, and validation proving no live
probes, downloads, uploads, local path search, arbitrary URL fetch, account
behavior, telemetry, or production claims were added by accident. Public Search
Result Card Contract v0 is the governed `results[]` card contract. Public
Search Safety / Abuse Guard v0 now constrains the local runtime and still blocks
hosted public exposure until the runtime readiness checklist is satisfied.
Public Search Rehearsal v0 now records local/prototype evidence for this
contract under `control/audits/public-search-rehearsal-v0/`, including safe
query results, blocked request results, static handoff review, public-alpha
review, and contract alignment. The rehearsal does not make `/search` or
`/api/v1/search` hosted, does not enable live probes, and does not add
downloads, installs, uploads, local path search, accounts, telemetry, or
external source calls.
Source Pack Contract v0 defines a future validated source metadata input
format. Source packs are not imported by the current public search runtime and
do not grant live connector behavior. A future import milestone must preserve
`local_index_only`, public-safe records, disabled downloads/uploads/local paths,
and checksum/rights/privacy validation before any source pack can influence
public search results.
Evidence Pack Contract v0 defines a future validated claim/observation input
format. Evidence packs are not imported by the current public search runtime,
do not make evidence canonical truth, and do not grant live fetch behavior.
Future public search use must pass review, redaction, checksum, rights/privacy,
snippet-limit, and conflict-handling gates before evidence-pack records can
affect result-card evidence.
Index Pack Contract v0 defines a future validated index coverage and
record-summary metadata format. Index packs are not imported or merged by the
current public search runtime, do not export raw SQLite or local cache data, do
not make index summaries canonical truth, and do not grant hosted ingestion or
live fetch behavior. Future public search use must pass review, redaction,
source/evidence comparison, checksum, rights/privacy, and conflict-handling
gates before index-pack summaries can affect public search results.
Contribution Pack Contract v0 defines a future validated review-candidate
wrapper for proposed changes and referenced packs. Contribution packs are not
imported by the current public search runtime, do not upload or accept records,
do not make contributions canonical truth, and do not grant moderation,
identity, live fetch, or master-index authority. Future public search use must
wait for Master Index Review Queue Contract v0-governed review and accepted
public records.
Source/Evidence/Index Pack Import Planning v0 keeps future pack import local
and validate-only first. Validated or quarantined packs have no public-search
impact by default and must not affect `local_index_only` search until a later
explicit import/index milestone adds an opt-in local mode.
AI Provider Contract v0 does not enable AI in public search. Public search
remains `local_index_only`; model reranking, AI query expansion, embeddings,
generated snippets, remote model calls, and AI evidence acceptance remain
future/deferred and require separate approval.
Typed AI Output Validator v0 does not change public search. It validates
standalone typed AI output examples offline and does not enable generated
snippets, model calls, query expansion, reranking, local-index mutation, or
public API output changes.
Pack Import Report Format v0 does not change public search. It records future
validate-only pack validation outcomes and hard false mutation fields, but does
not import packs, stage packs, mutate local indexes, upload, or mutate public
search or the master index.

Public Search Index Builder v0 now supplies the preferred local_index_only
input bundle for the current local/prototype public-search runtime. The bundle
lives under `data/public_index` and contains public-safe JSON/NDJSON documents,
source coverage, stats, and checksums generated from controlled repo fixtures
and recorded metadata only. Public requests still cannot choose an index path,
store root, local path, URL, live source, or credential. Missing or stale index
artifacts are build/validation problems, not permission to fan out to live
sources.

Static Site Search Integration v0 publishes
`site/dist/data/search_config.json` and
`site/dist/data/public_index_summary.json` so the static site can describe the
search path honestly. The default backend status is `backend_unconfigured`,
hosted form submission remains disabled, and no hosted URL may be surfaced
until operator evidence verifies it.

## Out Of Scope

This contract and local runtime do not implement hosted backend deployment,
live source probes, Internet Archive calls, Google
queries, arbitrary URL fetch, crawling, downloads, installers, uploads,
accounts, telemetry, native clients, relay runtime, snapshot reader runtime,
TLS, auth, rate limiting, process management, custom domains, production API
stability, or production readiness.
## P58 Local Hosted Rehearsal

The P58 rehearsal starts the hosted wrapper locally and checks the public API
routes over HTTP. It verifies request limits and blocked parameters without
claiming that the API is hosted or approved for production use.

## P59 Query Observation Boundary

P59 adds `contracts/query/query_observation.v0.json` for future query
intelligence. Public search routes remain unchanged in P59: they do not write
query observations, telemetry events, shared result caches, miss ledgers, probe
jobs, candidate-index records, local indexes, or master-index records.

## P60 Shared Result Cache Boundary

P60 adds `contracts/query/search_result_cache_entry.v0.json` for future shared
query/result cache entries. Public search routes remain unchanged: they do not
read or write result cache entries, persist cache state, publish cache entries,
write miss ledgers or search needs, enqueue probes, mutate candidate indexes,
or mutate master-index records.

## P61 Search Miss Ledger Boundary

P61 adds `contracts/query/search_miss_ledger_entry.v0.json` for future scoped
miss records. Public search routes remain unchanged: they do not write miss
ledger entries, persist ledger state, create search needs, enqueue probes,
mutate result caches, mutate candidate indexes, or mutate master-index records.

## P62 Search Need Record Boundary

P62 adds `contracts/query/search_need_record.v0.json` for future scoped
unresolved needs. Public search routes remain unchanged: they do not write need
records, persist need state, claim demand counts, enqueue probes, mutate result
caches or miss ledgers, mutate candidate indexes, or mutate master-index
records.

## P63 Probe Queue Boundary

P63 adds `contracts/query/probe_queue_item.v0.json` for future policy-gated
probe planning. Public search routes remain unchanged: they do not create queue
items, persist queue state, execute probes, call live sources, mutate source
caches, mutate evidence ledgers, mutate candidate indexes, or mutate
master-index records.
## P64 Candidate Index Note

The public search API does not expose candidate creation, candidate lookup,
candidate ranking, candidate path selection, candidate promotion, source-cache
mutation, evidence-ledger mutation, or master-index mutation in P64.

## P65 Candidate Promotion Boundary

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Future public search no-result/query-intelligence integration may include a query privacy and poisoning guard decision projection, but P67 is contract-only. Current public search does not persist guard decisions, mutate query observations/cache/miss/need/probe/candidate/known absence records, track accounts, track IPs, or export telemetry.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.

## Source Sync Worker v0 Relation

Source Sync Worker Contract v0 is future/contract-only. It may later consume probe queue and demand dashboard signals to plan approved, bounded source sync jobs, but P69 adds no connector runtime, source calls, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or index mutation.

## P70 Source Cache And Evidence Ledger Relation

Public search APIs do not write source cache records or evidence ledger records in P70. Public queries must not fan out live to source sync, source cache, or evidence ledger mutation.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/PUBLIC_SEARCH_API_CONTRACT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->
