# Public Data Contract

Public data files are registered in
`control/inventory/publication/public_data_contract.json`.

Field-level stability is governed by
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md` and the review pack under
`control/audits/public-data-contract-stability-review-v0/`. File-level
`stable_draft` means a generated JSON file is acceptable for cautious pre-alpha
clients, not that every nested field is stable. Future clients must consume
only the field paths marked `stable_draft` unless they deliberately
version-pin experimental fields.

Every public data entry must declare:

- `path`
- `status`
- `stability`
- `schema_version`
- `producer`
- `source_inputs`
- `generated_by`
- `consumer_profiles`
- `contains_live_data`
- `contains_external_observations`
- `safe_for_static_hosting`
- `notes`

Public JSON fields are compatibility-sensitive. New generated data should carry
a `schema_version`, avoid undocumented fields, and avoid implying live backend
availability unless capability flags explicitly enable it in a later hosted
backend milestone.

No live claims without source. No public data file may claim live source
coverage, external comparison results, or public deployment unless a repo source
records that evidence.

Implemented generated public data files include:

- `/data/site_manifest.json`
- `/data/page_registry.json`
- `/data/source_summary.json`
- `/data/eval_summary.json`
- `/data/route_summary.json`
- `/data/build_manifest.json`

They are produced by `scripts/generate_public_data_summaries.py` and mirrored
into `site/dist/data/` by `site/build.py`. They remain `stable_draft`, static,
and pre-alpha. They are not a live API, do not include live data, and do not
record external observations. Public JSON is not a production API and carries
no production stability guarantee.
Static Artifact Promotion Review v0 keeps these files under the active
repo-local `site/dist/data/` artifact and does not treat them as deployment
success evidence while GitHub Actions status is unverified.

Custom Domain / Alternate Host Readiness v0 adds static host readiness fields
to `/data/site_manifest.json` and readiness validation provenance to
`/data/build_manifest.json`. These fields describe future host portability
only; they do not configure DNS, add a `CNAME`, activate an alternate host, or
claim deployment success.

Live Backend Handoff Contract v0 adds disabled live capability summaries and
reserved `/api/v1` endpoint summaries to `/data/site_manifest.json`, plus
validation provenance to `/data/build_manifest.json`. These fields are static
contract metadata only. They do not make `/api/v1` live, do not expose a live
API, and do not change the `stable_draft` pre-alpha posture of public JSON.

Live Probe Gateway Contract v0 adds disabled source-probe gateway summaries to
`/data/site_manifest.json` and validation provenance to
`/data/build_manifest.json`. These fields describe future policy only. They do
not implement live probes, call external sources, fetch URLs, enable downloads,
or turn static JSON into a live probe API.

Public Search API Contract v0 adds contract-only public-search route summaries
to `/data/site_manifest.json` and validation provenance to
`/data/build_manifest.json`. These fields describe future `local_index_only`
search envelopes only. They do not make `/search` or `/api/v1/search` live,
host a backend, enable live probes, add downloads, installs, uploads, local
path search, arbitrary URL fetch, or turn static JSON into a live search API.
Public Search Result Card Contract v0 adds a hand-authored API schema and
examples for future result cards. It does not add live public-data output,
search runtime output, downloads, installers, execution, uploads, malware-safety
claims, rights-clearance claims, or production API stability.

Compatibility Surface Strategy v0 records surface capability and route matrix
inputs for public data consumers. These fields describe which static
projections exist now and which app, API, snapshot, relay, and native-client
surfaces remain future/deferred. They do not make public JSON a production API,
implement snapshots, add relay services, start native app projects, make
`/api/v1` live, or enable live probes.

Signed Snapshot Format v0 adds snapshot-format contract metadata to
`/data/site_manifest.json` and validation provenance to
`/data/build_manifest.json`. These fields describe the repo-local seed example
under `snapshots/examples/static_snapshot_v0/` and keep the public
`/snapshots/` route future/deferred. They do not publish production signed
snapshots, add real signing keys, add executable downloads, implement relay or
native-client runtime behavior, make public JSON a production API, or enable
live backend/probe behavior.

Relay Surface Design v0 adds relay design metadata to `/data/site_manifest.json`
and validation provenance to `/data/build_manifest.json`. These fields describe
future local/LAN relay policy only. They do not implement a relay runtime,
protocol server, network listener, private data exposure, live-probe passthrough,
write/admin route, or old-client protocol bridge.

Implemented file-tree public data files include:

- `/files/manifest.json`
- `/files/index.txt`
- `/files/SHA256SUMS`

They are produced by `scripts/generate_compatibility_surfaces.py` from
`site/dist/data/*.json`. They are static file-tree seed artifacts only: no
live data, no external observations, no executable downloads, and no signed
snapshot guarantee.

Implemented static demo data files include:

- `/demo/data/demo_snapshots.json`

This file is produced by `scripts/generate_static_resolver_demos.py` from
governed public data summaries and fixture-backed Python-oracle outputs. It is a
static demo manifest only: no live backend, no live search, no live API, no
external observations, and no production resolver guarantee.

The current `site/dist/site_manifest.json` is an implemented generated static
artifact manifest, not the final generated public data layout. The root manifest
and `/data/site_manifest.json` are intentionally separate: the root manifest
describes the page pack, while the `/data/` manifest summarizes static public
data for future clients.
