# Public Search Safety And Abuse Guard v0

Status: implemented as policy, contract, and local runtime guardrails.

Public Search Safety / Abuse Guard v0 defines the safety, abuse, privacy,
boundedness, and operator guardrails required by Local Public Search Runtime
v0. Local/prototype `/search`, `/api/v1/search`, `/api/v1/query-plan`,
`/api/v1/status`, `/api/v1/sources`, and `/api/v1/source/{source_id}` now use
these guardrails. This milestone still does not add rate-limit middleware,
auth, sessions, telemetry, logging runtime, backend hosting, live probes,
downloads, installers, execution, uploads, local path search, or deployment
provider configuration.
It does not enable live probes.

## P57 Safety Evidence

Public Search Safety Evidence v0 adds executable local evidence for this guard.
`python scripts/run_public_search_safety_evidence.py` exercises the hosted
wrapper in-process, verifies safe queries, rejects 32 blocked request cases,
checks limits/status/static handoff/public index posture, and records that edge
rate-limit evidence remains operator-gated. It adds no live probes, downloads,
uploads, installs, accounts, telemetry, arbitrary URL fetching, hosted
deployment, or production claim.

## Why This Exists

Public search accepts user input. The repo needs fixed boundaries for request
size, result count, source policy, privacy, disabled modes, disabled actions,
and operator controls before local prototype routes can exist and before any
hosted rehearsal can be considered.

The first allowed mode remains `local_index_only`:

```text
public query
  -> query planner
  -> controlled local index
  -> public result-card envelope
  -> source/evidence/compatibility/absence response
```

It must not become live external fanout, arbitrary URL fetch, local filesystem
search, downloads, installers, uploads, accounts, telemetry by default, or
unbounded query/result behavior.

## Policy Inventory

The machine-readable policy lives at:

```text
control/inventory/publication/public_search_safety.json
```

The policy records `status: local_runtime_guard_active`,
`local_public_search_runtime_implemented: true`,
`hosted_public_search_runtime_implemented: false`, and
`no_hosted_public_search_live: true`.

Hosted Public Search Wrapper v0 adds a local/prototype wrapper around the same
guarded public search API. The wrapper keeps `local_index_only`, no live probes,
no downloads, no uploads, no local paths, no arbitrary URL fetch, no telemetry,
and no accounts; hosted deployment evidence remains a later operator step.

## Allowed Mode

The only allowed v0 mode is:

- `local_index_only`

Disabled modes are:

- `live_probe`
- `live_federated`
- `arbitrary_url_fetch`
- `local_path_search`
- `upload_search`
- `download_or_install`

## Request, Result, And Time Limits

Policy defaults for Local Public Search Runtime v0 are:

- maximum query length: 160 characters
- minimum query length after trim: 1 character
- default result limit: 10
- maximum result limit: 25
- maximum include items: 8
- maximum request body bytes: 8192
- v0 request method: GET
- POST JSON body: future only
- maximum runtime target: 3000 ms
- checked sources in v0: controlled local index only
- live sources in v0: 0

These are local runtime bounds and hosted-exposure targets, not production
middleware.

## Forbidden Parameters

Public search must reject:

- `index_path`
- `store_root`
- `run_store_root`
- `task_store_root`
- `memory_store_root`
- `local_path`
- `path`
- `file_path`
- `directory`
- `root`
- `url`
- `fetch_url`
- `crawl_url`
- `source_url`
- `download`
- `install`
- `execute`
- `upload`
- `user_file`
- `source_credentials`
- `auth_token`
- `api_key`
- `live_probe`
- `live_source`
- `network`
- `arbitrary_source`

The runtime owns the local index root. A caller must never provide an index
path, store root, source URL, local path, credentials, or uploaded file to
public search.

## Forbidden Behaviors

Public search v0 forbids:

- arbitrary URL fetching
- live external source fanout
- Google scraping
- Internet Archive live calls
- Wayback live calls
- GitHub live calls
- package registry live calls
- local filesystem search
- caller-provided index paths
- caller-provided store roots
- downloads
- installs
- executable launch
- uploads
- account or session requirement
- telemetry by default
- private path leakage
- credential submission
- raw source payload return
- unbounded query or result behavior

## Error Mapping

The guard uses the Public Search API Contract v0 error envelope. Required codes
include:

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
- `bad_request`

Local path and root parameters should map to `local_paths_forbidden`. Download
requests map to `downloads_disabled`. Install or execute requests map to
`installs_disabled`. Upload or user-file requests map to `uploads_disabled`.
Live-probe or live-source requests map to `live_probes_disabled`.

## Logging And Privacy

Telemetry is not implemented and defaults off. Raw query logging is disabled by
default for the static/public-alpha contract. Any future hosted rehearsal may
use only short-retention sanitized logs after a separate privacy review.

Public search must not log private paths, credentials, user files, source
secrets, raw source payloads, or account identifiers. IP retention, user-agent
logging, and aggregate metrics remain future review items. Manual observations
remain human-entered evidence, not telemetry. Query logs must not be uploaded to
external services by default.

## Operator Controls

Hosted public search must provide controls equivalent to:

- `EUREKA_PUBLIC_SEARCH_MODE=local_index_only`
- `EUREKA_ALLOW_LIVE_PROBES=0`
- `EUREKA_ALLOW_DOWNLOADS=0`
- `EUREKA_ALLOW_INSTALLS=0`
- `EUREKA_ALLOW_LOCAL_PATHS=0`
- `EUREKA_ALLOW_USER_UPLOADS=0`
- `EUREKA_ALLOW_TELEMETRY=0`
- `EUREKA_MAX_QUERY_LEN=160`
- `EUREKA_MAX_RESULTS=25`
- `EUREKA_SEARCH_TIMEOUT_MS=3000`
- `EUREKA_PUBLIC_SEARCH_ENABLED=0`
- `EUREKA_OPERATOR_KILL_SWITCH=1`

The operator kill switch is required before any hosted wrapper can be exposed.
These flags remain hosted-runtime requirements. This milestone adds no process
manager, provider configuration, rate-limit middleware, or deployment runtime.

## Public Alpha And Static Site

Public Alpha Safe Mode remains non-production and local. It already blocks live
probes, caller-provided local paths, downloads, fixture byte fetches, user
storage, deployment approval, and production readiness by default. Local Public
Search Runtime v0 may expose `/api/v1/search` in public-alpha only as
local/prototype backend runtime with `local_index_only` validation. Hosted
public search is not live.

GitHub Pages remains static-only. `site/dist` may describe this policy but must
not add a search form, claim hosted search exists, or imply backend deployment.

## Live Backend And Live Probe Relationships

Live Backend Handoff Contract v0 remains future/reserved for hosted runtime.
Local Public Search Runtime v0 does not create hosted routes.

Live Probe Gateway Contract v0 remains disabled by default. `local_index_only`
does not call Internet Archive, Wayback, Google, GitHub, package registries, or
any external source.

## Action And Privacy Policy Relationships

Native Action / Download / Install Policy v0 keeps downloads, mirrors, install
handoff, package-manager handoff, execution, restore, rollback, and uploads
blocked or future-gated.

Native Local Cache / Privacy Policy v0 keeps private cache, private file
ingestion, telemetry, accounts, cloud sync, diagnostics upload, source
credentials, and private path exposure disabled by default.

## Runtime Prerequisites

After Local Public Search Runtime v0, the runtime readiness checklist records
which local gates are satisfied and which hosted gates remain blocked:

```text
docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md
```

The key hosted gates are: API contract passes, result-card contract passes,
safety guard passes, generated public index exists and validates, local index
root remains server-owned, no local path params, no live probes, no downloads,
no uploads, stable error mapping, defined HTML/JSON behavior, operator flags,
no production claim, and accepted logging/privacy posture.

## Still Future

Still future or blocked until explicit approval:

- hosted backend
- rate-limit middleware
- auth, accounts, sessions, TLS, process management
- live probes or external source fanout
- local filesystem search
- downloads, installers, execution, mirrors, uploads
- telemetry/logging runtime
- native clients, relay runtime, snapshot reader runtime
- production API stability or production readiness

Implemented static publication only:

- Public Search Static Handoff v0 adds no-JS `site/dist/search.html`,
  `lite/search.html`, `text/search.txt`, `files/search.README.txt`, and
  `data/search_handoff.json`; it does not configure hosted search or weaken the
  disabled live-probe/download/upload/local-path posture.
- Public Search Rehearsal v0 records local/prototype route coverage, safe-query
  evidence, blocked-request evidence, static handoff review, public-alpha
  review, and contract alignment without deploying hosted search or enabling
  live probes, downloads, installs, uploads, local path search, accounts,
  telemetry, or external calls.
- Public Search Index Builder v0 adds the generated `data/public_index` bundle
  and validates it without live source calls, private path ingestion,
  executable payloads, downloads, uploads, or master-index mutation.
## P58 Hosted Rehearsal Evidence

P58 starts the hosted wrapper locally and verifies the same safety posture over
HTTP: `local_index_only`, safe status routes, safe query responses, and blocked
dangerous parameters. The rehearsal does not add live probes, downloads,
uploads, accounts, telemetry, arbitrary URL fetch, or edge rate-limit claims.

## Query Intelligence Safety Boundary

P59, P60, P61, and P62 add contract-only query observation, shared result
cache, search miss ledger, and search need shapes. They do not add telemetry,
persistent query logging, runtime cache writes, runtime ledger writes, runtime
need storage, demand-count runtime, probe enqueueing, candidate-index mutation,
local-index mutation, master-index mutation, or hosted query-intelligence
runtime.

P63 adds contract-only probe queue shapes. It does not add a runtime queue,
probe execution, live source calls, source-cache mutation, evidence-ledger
mutation, candidate-index mutation, search-need mutation, local-index mutation,
master-index mutation, or any change to the public-search blocked-parameter
posture.
## P64 Candidate Index Note

Candidate records are not public search authority in P64. Safety and abuse
guards must continue to block caller-selected candidate paths, source roots,
local paths, URLs, live sources, uploads, downloads, installs, telemetry, and
master-index mutation in any future candidate-aware work.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

P67 Query Privacy and Poisoning Guard v0 is contract-only and complements the existing public search safety posture. It does not implement WAF behavior, rate limiting, telemetry, account tracking, IP tracking, runtime moderation, public query logging, or hosted abuse protection. Future public search may reference guard decisions only after explicit runtime wiring and verification.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->
