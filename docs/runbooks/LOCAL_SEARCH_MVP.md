# Local Search MVP

This runbook covers `EUREKA-USABLE-LOCAL-SEARCH-MVP-00-P0`, the local-only
developer search slice and the `LOCAL-METADATA-FALLBACK-E2E-DEMO-00`
fixture-backed fallback demo. It also covers `IA-METADATA-LIVE-OPTIN-00`, the
developer-only live IA metadata opt-in, `LOCAL-SEARCH-INDEX-BUILDER-00`, the
deterministic local index builder, `REVIEWED-RECORD-MATERIALIZATION-00`, the
local generated review loop that proves review can change search, and
`WORKBENCH-OPERATOR-ROUTES-00`, the local/private Workbench P0, and
`PUBLIC-READONLY-WEB-ALPHA-00`, the local public-alpha read-only surface.

## CLI

```powershell
python scripts/eureka_search.py --all --format text --metadata-fallback ia_fixture
python scripts/eureka_search.py "old blue FTP client for XP" --format text --metadata-fallback ia_fixture
python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format json --metadata-fallback ia_fixture
python scripts/eureka_search.py "driver for Win98" --format text --metadata-fallback ia_fixture
```

Useful flags:

- `--format text|json`
- `--metadata-fallback none|ia_fixture|ia_live`
- `--allow-live-metadata`
- `--metadata-timeout SECONDS`
- `--metadata-budget N`
- `--index none|local`
- `--index-path PATH`
- `--limit N`
- `--show-evidence`
- `--show-debug`

## Local Server

```powershell
python scripts/run_eureka_local.py --smoke --metadata-fallback ia_fixture
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --metadata-fallback ia_fixture
```

Routes:

- `http://127.0.0.1:8765/`
- `http://127.0.0.1:8765/health`
- `http://127.0.0.1:8765/api/status`
- `http://127.0.0.1:8765/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `http://127.0.0.1:8765/search?q=old%20blue%20FTP%20client%20for%20XP`

## Fallback Modes

- `none`: run the local path without IA metadata fallback.
- `ia_fixture`: use committed IA-shaped metadata fixtures only. This mode does
  not use live network access, downloads, file fetches, or source probes.
- `ia_live`: use the governed Internet Archive metadata provider only when
  `--allow-live-metadata` is also present. Without that flag, Eureka fails
  closed with `policy_blocked` and performs no live request.

## Local Search Index

Build a deterministic local demo index:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json
python scripts/eureka_index.py stats --index .eureka/local_search_index.json
python scripts/eureka_index.py validate --index .eureka/local_search_index.json
```

Search through the built index without metadata fallback:

```powershell
python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format text --index local --index-path .eureka/local_search_index.json --metadata-fallback none
python scripts/eureka_search.py "driver for Win98" --format text --index local --index-path .eureka/local_search_index.json --metadata-fallback none
python scripts/run_eureka_local.py --smoke --index local --index-path .eureka/local_search_index.json --metadata-fallback none
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --index local --index-path .eureka/local_search_index.json --metadata-fallback none
```

The generated `.eureka/local_search_index.json` file is a local developer
artifact and is ignored by git. The `local_demo` source uses committed local
fixtures and hard-query demo data only. Index building performs no live network
calls, downloads, file fetching, Wayback replay, extraction, review
materialization, or public mutation.

Indexed fixture-derived records remain non-verified candidates, needs, near
misses, policy blocks, or unavailable states unless an existing reviewed source
already marked them as verified. The index improves local search behavior; it
does not create reviewed truth. Search requests read the index first when
`--index local` is enabled. If the index is missing or insufficient and
`--metadata-fallback none` is set, Eureka returns an honest need/unavailable
state. If `ia_fixture` or explicit `ia_live --allow-live-metadata` is enabled,
the governed fallback path can run after an index miss.

`/api/status` reports index mode, loaded state, path, document count, metadata
fallback mode, live metadata posture, and read-only/no-mutation flags. Search
responses report whether indexed results were used and how many documents were
loaded.

Troubleshooting local index:

- If validation fails, rebuild the index from `local_demo`.
- If search reports `index_loaded: false`, check `--index-path` and run
  `python scripts/eureka_index.py validate --index <path>`.
- If an indexed query returns `need`, the local demo corpus has no sufficient
  indexed match; refine the query or enable a governed metadata fallback.
- If results look stale, rebuild the local index after fixture or reviewed-data
  changes.

## Local Review Materialization

Build the base local index, list the deterministic candidate, accept it into
local generated review artifacts, rebuild a reviewed index, and search it:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/eureka_review.py candidates --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740"

python scripts/eureka_review.py accept --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740" --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl --reviewer local_demo --reason "P0 local review materialization demo"

python scripts/eureka_review.py stats --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl

python scripts/eureka_index.py build --source local_demo --reviewed-records .eureka/local_reviewed_records.jsonl --out .eureka/local_search_index.reviewed.json

python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format text --index local --index-path .eureka/local_search_index.reviewed.json --metadata-fallback none

python scripts/run_eureka_local.py --smoke --index local --index-path .eureka/local_search_index.reviewed.json --metadata-fallback none
```

The ledger and reviewed-record files under `.eureka/` are local generated
developer artifacts. They are useful for proving the loop from indexed candidate
to accepted local reviewed source lead, but they are not production review
state and are not public alpha data.

A local reviewed metadata/source-lead record is distinct from a verified
artifact. The materialized record uses `review_state=accepted` and
`record_state=reviewed`, while `artifact_verified`, `accepted_truth`, public
index mutation, and master index mutation remain false. Search reads reviewed
records only through the rebuilt local index; search requests do not mutate the
review ledger, reviewed records, local index, public index, or master index.

After rebuilding with `--reviewed-records`, `/api/status` reports
`reviewed_record_count` and `artifact_verified_count`. `/api/search` and
`/search` show the accepted local review state, the reviewed record id, the
review event id, source/evidence hints, and `artifact_verified: false`.

Troubleshooting local review materialization:

- If `candidates` returns no candidate, rebuild the base local index or refine
  the query.
- If `accept` fails with `candidate not found`, omit `--candidate-id` or copy an
  id from the `candidates` output.
- If reviewed-index build fails, validate the JSONL records and ensure each
  record has review ids, evidence hints, and `artifact_verified=false`.
- If search does not show the reviewed state, rebuild
  `.eureka/local_search_index.reviewed.json` with `--reviewed-records`.
- If generated files are missing, rerun the `accept` command; repeated accepts
  for the same candidate, reviewer, and decision are idempotent.

## Local Workbench Operator Routes

The local Workbench P0 wraps the same local index, review materialization, and
search service used by the CLI. It is disabled by default, token-gated when
enabled, and must run on a loopback host.

Build a local index and start the server with Workbench enabled:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --index local --index-path .eureka/local_search_index.json --metadata-fallback none --enable-workbench --workbench-token local-dev-token
```

The smoke command is:

```powershell
python scripts/run_eureka_local.py --smoke --index local --index-path .eureka/local_search_index.json --metadata-fallback none --enable-workbench --workbench-token local-dev-token
```

Useful local Workbench routes:

```text
http://127.0.0.1:8765/workbench?token=local-dev-token
http://127.0.0.1:8765/workbench/status?token=local-dev-token
http://127.0.0.1:8765/workbench/candidates?q=manual%20for%20Sound%20Blaster%20CT1740&token=local-dev-token
http://127.0.0.1:8765/workbench/review?q=manual%20for%20Sound%20Blaster%20CT1740&token=local-dev-token
http://127.0.0.1:8765/workbench/api/status?token=local-dev-token
http://127.0.0.1:8765/workbench/api/candidates?q=manual%20for%20Sound%20Blaster%20CT1740&token=local-dev-token
```

Accept a candidate through the JSON API:

```powershell
$body = @{
  query = "manual for Sound Blaster CT1740"
  reason = "Workbench P0 local accept demo"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/workbench/api/review/accept -Headers @{ "X-Eureka-Workbench-Token" = "local-dev-token" } -ContentType "application/json" -Body $body
```

After accept, the Workbench writes only the configured local generated ledger
and reviewed-record files, then rebuilds the configured local generated index.
Normal search should now show the reviewed/local accepted result first:

```text
http://127.0.0.1:8765/api/search?q=manual%20for%20Sound%20Blaster%20CT1740
http://127.0.0.1:8765/search?q=manual%20for%20Sound%20Blaster%20CT1740
```

The Workbench P0 token is a local development guard, not production
authentication. Do not bind Workbench to `0.0.0.0`; the server refuses
non-loopback hosts when Workbench is enabled. Workbench materialization keeps
`artifact_verified=false` and does not mutate canon, release state,
queue/current, source fixtures, official reviewed records, public indexes,
master indexes, or artifact gate counts.

Troubleshooting local Workbench:

- If `/workbench` says disabled, restart with `--enable-workbench`.
- If a route returns unauthorized, pass the token as `?token=...` for local
  HTML routes or `X-Eureka-Workbench-Token` for API requests.
- If candidates are missing, rebuild the local index or refine the query.
- If normal search looks stale, confirm the accept response reports
  `index_rebuilt=true` and that the server is using the same `--index-path`.
- If startup fails on `0.0.0.0`, restart on `127.0.0.1` or `localhost`.
- If rebuild fails, inspect the local reviewed-record JSONL file and rerun the
  base index build.

## Public Read-Only Web Alpha Mode

Public-alpha mode is a local public-style read-only surface over a reviewed
local index. It is not an internet deployment, staging rollout, public launch,
or public mutation path.

Build a reviewed local index:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/eureka_review.py accept --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740" --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl --reviewer local_demo --reason "Public alpha local reviewed seed"

python scripts/eureka_index.py build --source local_demo --reviewed-records .eureka/local_reviewed_records.jsonl --out .eureka/local_search_index.reviewed.json
```

Run the public-alpha smoke and local server:

```powershell
python scripts/run_eureka_local.py --smoke --public-alpha --index local --index-path .eureka/local_search_index.reviewed.json --metadata-fallback none

python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --index local --index-path .eureka/local_search_index.reviewed.json --metadata-fallback none
```

Public routes:

- `http://127.0.0.1:8765/`
- `http://127.0.0.1:8765/health`
- `http://127.0.0.1:8765/status`
- `http://127.0.0.1:8765/api/status`
- `http://127.0.0.1:8765/about`
- `http://127.0.0.1:8765/method`
- `http://127.0.0.1:8765/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `http://127.0.0.1:8765/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `http://127.0.0.1:8765/record/<id>`

Public-alpha mode requires `--index local`, a valid `--index-path`, and
`--metadata-fallback none`. It refuses `ia_live`, `--allow-live-metadata`,
`--enable-workbench`, and non-loopback hosts such as `0.0.0.0`. `/api/status`
reports `read_only=true`, `public_live_fanout=false`,
`live_metadata_enabled=false`, and `workbench_exposed=false` without exposing
local generated paths or tokens.

Public search pages show reviewed, candidate, need, near_miss,
policy_blocked, unavailable, and unknown states when present in the local
index. The Sound Blaster query should show the reviewed/local accepted result
first after the reviewed index is rebuilt. Use the `record_url` from
`/api/search` or the `View record` link from `/search` to verify
`/record/{id}`. Record pages show title, status, review state,
`artifact_verified`, evidence/source hints, missing information, safe next
action, and a public-safe provenance summary.

Public routes expose only safe read actions. They do not expose Workbench
links, review actions, accept/reject/promote controls, index rebuild controls,
live metadata calls, downloads, file fetching, Wayback replay, extraction,
install/emulation behavior, marketplace behavior, or public contribution
intake. Public-alpha search is read-only and does not mutate reviewed records,
review ledgers, local indexes, public indexes, master indexes, source fixtures,
gate counts, canon, release state, or queue/current.

Troubleshooting public alpha:

- If startup says a valid local index is required, build the reviewed index and
  validate it with `python scripts/eureka_index.py validate --index <path>`.
- If startup refuses `ia_live` or `--allow-live-metadata`, rerun with
  `--metadata-fallback none`; public-alpha mode does not expose live metadata.
- If startup refuses `--enable-workbench`, restart without Workbench; public
  alpha and Workbench are intentionally separate modes.
- If startup refuses `0.0.0.0`, use `127.0.0.1` or `localhost`; deployment is a
  later task.
- If the Sound Blaster result is not reviewed first, rebuild the index with
  `--reviewed-records .eureka/local_reviewed_records.jsonl`.
- If `/record/{id}` returns 404, copy a current `record_url` from
  `/api/search` after rebuilding the reviewed index.

## Fixture Metadata Fallback Demo

`ia_fixture` means Eureka asks a committed Internet Archive-shaped metadata
fixture after the local reviewed/index lookup is missing or insufficient. The
fixture can produce candidates, needs, near misses, unavailable states, or
policy blocks. It cannot produce verified truth.

CLI examples:

```powershell
python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format text --metadata-fallback ia_fixture
python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format json --metadata-fallback ia_fixture
python scripts/eureka_search.py "latest Firefox before XP support ended" --format text --metadata-fallback ia_fixture
python scripts/eureka_search.py "driver for Win98" --format text --metadata-fallback ia_fixture
```

API and HTML examples:

```text
http://127.0.0.1:8765/api/search?q=manual%20for%20Sound%20Blaster%20CT1740
http://127.0.0.1:8765/search?q=manual%20for%20Sound%20Blaster%20CT1740
```

The JSON response includes `fallback_summary`, `fallback_mode`,
`fallback_used`, `provider_family`, `source_observations`,
`non_verified_reason`, and `no_mutation`. The text and HTML views show the same
posture in human-readable form: fallback used or not used, source/evidence
hints, missing information, safe next action, and the non-verified state.

Fallback output is non-verified because fixture metadata is only a source
observation. It has not been reviewed, accepted into a ledger, materialized as a
reviewed record, or promoted into any reviewed/public/master index.

## Live IA Metadata Opt-In

Live IA metadata is off by default. It is local/developer-only, metadata-only,
and candidate/need/near-miss/unavailable/policy-blocked only. It never verifies
truth, writes reviewed records, mutates indexes, downloads files, fetches files,
replays Wayback, extracts content, installs software, or exposes public live
fanout.

CLI opt-in:

```powershell
python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format json --metadata-fallback ia_live --allow-live-metadata --metadata-timeout 8 --metadata-budget 3 --limit 5
python scripts/eureka_search.py "latest Firefox before XP support ended" --format text --metadata-fallback ia_live --allow-live-metadata --metadata-timeout 8 --metadata-budget 3 --limit 5
```

Missing opt-in fails closed:

```powershell
python scripts/eureka_search.py "manual for Sound Blaster CT1740" --format json --metadata-fallback ia_live
```

Local server opt-in:

```powershell
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --metadata-fallback ia_live --allow-live-metadata --metadata-timeout 8 --metadata-budget 3
```

The server keeps `127.0.0.1` as the safe default. Live metadata mode refuses
non-loopback hosts such as `0.0.0.0`.

Status and search routes:

```text
http://127.0.0.1:8765/api/status
http://127.0.0.1:8765/api/search?q=manual%20for%20Sound%20Blaster%20CT1740
http://127.0.0.1:8765/search?q=manual%20for%20Sound%20Blaster%20CT1740
```

`/api/status` reports `metadata_fallback`, `live_metadata_enabled`,
`provider_family`, `network_default`, `public_live_fanout`, timeout, and budget.
Search responses report `fallback_summary`, `fallback_mode`, `fallback_used`,
`provider_family`, `live_metadata_enabled`, `network_used`, `timeout_seconds`,
`budget`, `budget_used`, source observations, evidence/source hints,
`non_verified_reason`, and `no_mutation`.

Troubleshooting live opt-in:

- If the response is `policy_blocked` with `live_metadata_opt_in_missing`, add
  `--allow-live-metadata`.
- If the response is `unavailable` with `source_timeout`, retry later with a
  short timeout or use `ia_fixture`.
- If the response is `unavailable` with `fallback_budget_exceeded`, increase
  `--metadata-budget` above zero.
- If the network is unavailable, Eureka should still return a non-verified
  unavailable/need state rather than mutating truth.
- If the server refuses the host, use `127.0.0.1`, `localhost`, or `::1`.

## Statuses

- `verified`: existing local reviewed/index result only.
- `candidate`: useful lead that still requires review.
- `need`: missing scope, evidence, or user detail.
- `near_miss`: related lead that is not an identity match.
- `policy_blocked`: blocked by policy or review gate.
- `unavailable`: source or fixture path could not provide useful output.
- `unknown`: no reliable state yet.

## P0 Non-Goals

P0 does not add detail routes, Workbench routes, deployment packaging, public
alpha launch behavior, downloads, installs, emulation, reviewed-record
mutation, public-index mutation, or a new search architecture.

The fallback and live opt-in demos still defer persistent metadata cache,
advanced IA ranking, downloads, file fetching, Wayback replay, extraction,
ReviewLedger production materialization, production index service, advanced
ranking, live IA indexing, background refresh, Workbench operator routes,
public alpha behavior, deployment packaging, public live fanout,
official artifact gate updates, verified artifact evidence promotion, and
object/candidate/need/source/evidence detail routes.

## Troubleshooting

- If a CLI command cannot import repo modules, run it from the repo root.
- If port `8765` is busy, rerun the server with another `--port`.
- If a query returns `need`, refine the query or add reviewed source evidence.
- If a driver query returns a hardware-detail blocker, collect vendor, model,
  device ID or chipset, bus/interface, architecture, and exact OS version.
- If JSON output is too large, omit `--show-debug`.
