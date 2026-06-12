# Local Search MVP

This runbook covers `EUREKA-USABLE-LOCAL-SEARCH-MVP-00-P0`, the local-only
developer search slice and the `LOCAL-METADATA-FALLBACK-E2E-DEMO-00`
fixture-backed fallback demo. It also covers `IA-METADATA-LIVE-OPTIN-00`, the
developer-only live IA metadata opt-in.

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
alpha launch behavior, live IA metadata, downloads, installs, emulation,
reviewed-record mutation, public-index mutation, or a new search architecture.

The fallback and live opt-in demos still defer persistent metadata cache,
advanced IA ranking, downloads, file fetching, Wayback replay, extraction,
index building, review materialization, Workbench operator routes, public alpha
behavior, deployment packaging, public live fanout, and
object/candidate/need/source/evidence detail routes.

## Troubleshooting

- If a CLI command cannot import repo modules, run it from the repo root.
- If port `8765` is busy, rerun the server with another `--port`.
- If a query returns `need`, refine the query or add reviewed source evidence.
- If a driver query returns a hardware-detail blocker, collect vendor, model,
  device ID or chipset, bus/interface, architecture, and exact OS version.
- If JSON output is too large, omit `--show-debug`.
