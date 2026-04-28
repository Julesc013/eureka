# Public Data Contract

Public data files are registered in
`control/inventory/publication/public_data_contract.json`.

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
record external observations.

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

Implemented file-tree public data files include:

- `/files/manifest.json`
- `/files/index.txt`
- `/files/SHA256SUMS`

They are produced by `scripts/generate_compatibility_surfaces.py` from
`public_site/data/*.json`. They are static file-tree seed artifacts only: no
live data, no external observations, no executable downloads, and no signed
snapshot guarantee.

Implemented static demo data files include:

- `/demo/data/demo_snapshots.json`

This file is produced by `scripts/generate_static_resolver_demos.py` from
governed public data summaries and fixture-backed Python-oracle outputs. It is a
static demo manifest only: no live backend, no live search, no live API, no
external observations, and no production resolver guarantee.

The current `public_site/site_manifest.json` is an implemented static artifact
manifest, not the final generated public data layout. Static Site Generation
Migration v0 also emits a generated `site/dist/site_manifest.json` for
validation. The root manifest and `/data/site_manifest.json` are intentionally
separate: the root manifest describes the page pack, while the `/data/` manifest
summarizes static public data for future clients.
