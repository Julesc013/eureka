# Public Search Local-Index-Only Mode

Status: implemented for Local Public Search Runtime v0 as local/prototype backend runtime only.

`local_index_only` is the first allowed public search execution mode. It is a
local/prototype backend runtime mode, not a hosted API. Public Search Static
Handoff v0 now exposes a static/no-JS entry point to this mode, but the handoff
does not run search on GitHub Pages. The mode keeps public search bounded to
controlled local index records owned by the Eureka runtime.

## Allowed Shape

`local_index_only` search may:

- accept a bounded public query with a 160 character maximum;
- use a controlled local index owned by the public-search runtime;
- return at most 25 results in contract v0, defaulting to 10;
- expose result lanes, user-cost hints, compatibility summaries, evidence
  summaries, source summaries, warnings, and bounded absence reports;
- emit result cards governed by Public Search Result Card Contract v0;
- produce `standard_web`, `lite_html`, `text`, `api_client`, `snapshot`, and
  `native_client` projections;
- return the stable error envelope defined by Public Search API Contract v0.

Operational summary: no live probes, no downloads, no installs, no uploads, no
caller-provided local paths, and no arbitrary URL fetches are allowed.

The mode may read only governed public/local-index records selected by the
runtime. It must not accept caller-provided index roots, store
roots, local filesystem paths, URLs, credentials, uploaded files, or source
secrets.

## Explicitly Forbidden In v0

`local_index_only` does not allow:

- live external calls;
- live Internet Archive, Wayback, Google, GitHub, package-registry, or search
  engine queries;
- arbitrary URL fetch;
- scraping, crawling, or source fanout;
- local path search or private file ingestion;
- downloads, executable mirrors, installer handoff, or package-manager handoff;
- uploads, accounts, telemetry, cloud sync, auth credentials, or private user
  state;
- executable trust claims, rights-clearance claims, or malware-scan claims;
- production API stability or production readiness claims.

## Error And Safety Expectations

Invalid queries should use `query_required` or `query_too_long`. Unsupported
modes, profiles, and include values should use the corresponding unsupported
error codes. Forbidden fields should use `forbidden_parameter` or the more
specific `local_paths_forbidden`, `downloads_disabled`, `installs_disabled`,
`uploads_disabled`, or `live_probes_disabled` codes.

Public Search Safety / Abuse Guard v0 now defines and constrains this local
runtime. This local-index mode still does not implement rate limiting, TLS,
auth, abuse detection, process management, logging, or hosted deployment.

Public Search Safety / Abuse Guard v0 is now implemented as guardrails in
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md` and
`control/inventory/publication/public_search_safety.json`. Local Public Search
Runtime v0 satisfies the first local route gate; hosted public exposure still
must satisfy `docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`.

Public Search Rehearsal v0 now records local/prototype evidence for this mode
under `control/audits/public-search-rehearsal-v0/`. The rehearsal exercises
safe queries, no-result responses, blocked unsafe parameters, static handoff
honesty, and public-alpha posture without hosted deployment, live probes,
downloads, installs, uploads, local path search, accounts, telemetry, or
external calls.

Hosted Public Search Wrapper v0 now exposes this same mode through
`scripts/run_hosted_public_search.py` for local rehearsal and later
operator-controlled hosting. It does not change the mode contract or enable
live probes, downloads, uploads, local paths, arbitrary URL fetch, accounts,
telemetry, or source connectors.

Public Search Safety Evidence v0 records local proof that this mode is
preserved across safe queries, blocked dangerous parameters, limit/status
checks, the hosted-wrapper in-process harness, static handoff files, and the
generated public index. That evidence remains local/public-alpha only and does
not make a hosted backend live.

Public Search Index Builder v0 now provides the preferred controlled input for
this mode under `data/public_index`. The runtime loads
`search_documents.ndjson` when present and reports
`index_status=generated_public_search_index`; hosted-wrapper config validation
requires the generated public index to exist. Local development may still fall
back to the old in-memory demo catalog if the generated index is absent, but
public or hosted-safe checks should treat a missing index as drift to repair,
not as permission to read private paths or call live sources.

## Privacy And Logging Notes

Future public search logs must avoid private local paths, credentials, uploaded
payloads, user files, raw source payloads, and account identifiers. Query
logging remains a future policy decision and must be bounded/redacted before any
hosted use. Static GitHub Pages publication remains separate from hosted backend
runtime evidence.

## Relationship To Other Surfaces

Static `site/dist` remains the active publication artifact and does not host
live search. Public data, lite, text, files, and demo surfaces now include a
search handoff page, text/file-tree notes, and `data/search_handoff.json`; they
may describe local runtime usage, but they must not claim hosted public search
exists. Native
clients, relay surfaces, and snapshots may consume stable fields only after
their own contracts allow it.
## P58 Hosted Rehearsal

P58 confirms that the hosted wrapper can serve the public search route surface
locally while preserving `local_index_only` mode. Public requests still cannot
select index paths, store roots, local paths, URLs, credentials, live sources,
or live probe behavior.
## Query Observation Boundary

P59 Query Observation Contract v0 keeps public query learning contract-only.
`local_index_only` search does not write query observations, telemetry events,
shared query/result cache entries, miss ledger entries, probe jobs, candidate
records, local indexes, or master-index records.

P60 Shared Query/Result Cache v0, P61 Search Miss Ledger v0, and P62 Search
Need Record v0 keep reusable summaries, scoped misses, and scoped unresolved
needs contract-only. `local_index_only` search does not read or write result
cache entries, write miss ledger entries, create search needs, claim demand
counts, enqueue probes, mutate candidate records, mutate local indexes, or
mutate master-index records.

P63 Probe Queue v0 keeps future probe planning contract-only. `local_index_only`
search does not create queue items, execute probes, call live sources, mutate
source caches or evidence ledgers, mutate candidate records, or relax the
server-owned index and source boundaries.
