# Public Data Contract

Public data files are registered in
`control/inventory/publication/public_data_contract.json`.

Every public data entry must declare:

- `path`
- `status`
- `stability`
- `schema_version`
- `producer`
- `consumer_profiles`
- `contains_live_data`
- `contains_external_observations`
- `safe_for_static_hosting`
- `notes`

Public JSON fields are compatibility-sensitive. New generated data should carry
a `schema_version`, avoid undocumented fields, and avoid implying live backend
availability unless a later live backend handoff contract says so.

No live claims without source. No public data file may claim live source
coverage, external comparison results, or public deployment unless a repo source
records that evidence.

Planned public data files include:

- `/data/site_manifest.json`
- `/data/page_registry.json`
- `/data/source_summary.json`
- `/data/eval_summary.json`
- `/data/route_summary.json`
- `/data/build_manifest.json`
- `/files/index.txt`
- `/files/SHA256SUMS`

The current `public_site/site_manifest.json` is an implemented static artifact
manifest, not the final generated public data layout.

