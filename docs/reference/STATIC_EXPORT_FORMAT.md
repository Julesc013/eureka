# Static Export Format

Current static export:

```text
public_site/
  index.html
  status.html
  sources.html
  evals.html
  demo-queries.html
  limitations.html
  roadmap.html
  local-quickstart.html
  site_manifest.json
  data/
  lite/
  text/
  files/
  demo/
  assets/
```

`public_site/` is the active static public artifact. GitHub Pages Deployment
Enablement v0 uploads this directory as-is after validation.

Generated v0 export:

```text
site/
  pages/
  templates/
  data/
  assets/
  build.py
  validate.py
site/dist/
  index.html
  status.html
  sources.html
  evals.html
  demo-queries.html
  limitations.html
  roadmap.html
  local-quickstart.html
  site_manifest.json
  data/
  lite/
  text/
  files/
  demo/
  assets/
```

Static Site Generation Migration v0 creates this stdlib-only generator shape.
The generated `site/dist/` output is validation evidence and is not the GitHub
Pages artifact yet.

Generated Public Data Summaries v0 adds:

```text
public_site/data/
  site_manifest.json
  page_registry.json
  source_summary.json
  eval_summary.json
  route_summary.json
  build_manifest.json
site/dist/data/
  site_manifest.json
  page_registry.json
  source_summary.json
  eval_summary.json
  route_summary.json
  build_manifest.json
```

These are deterministic static JSON summaries, not live API routes.

Lite/Text/Files Seed Surfaces v0 adds:

```text
public_site/lite/
  index.html
  sources.html
  evals.html
  demo-queries.html
  limitations.html
  README.txt
public_site/text/
  index.txt
  sources.txt
  evals.txt
  demo-queries.txt
  limitations.txt
  README.txt
public_site/files/
  index.html
  index.txt
  README.txt
  manifest.json
  SHA256SUMS
  data/README.txt
```

`site/build.py` emits matching validation copies into `site/dist/lite/`,
`site/dist/text/`, and `site/dist/files/`. These are static compatibility
surfaces, not live search, executable downloads, production signed snapshots, relay
behavior, or native-client runtime.

Static Resolver Demo Snapshots v0 adds:

```text
public_site/demo/
  index.html
  query-plan-windows-7-apps.html
  result-member-driver-inside-support-cd.html
  result-firefox-xp.html
  result-article-scan.html
  absence-example.html
  comparison-example.html
  source-example.html
  eval-summary.html
  README.txt
  data/demo_snapshots.json
```

`site/build.py` emits matching validation copies into `site/dist/demo/`. These
are static, fixture-backed resolver examples. They are not live search, a live
API, external observations, backend hosting, or production resolver behavior.

Signed Snapshot Format v0 adds a repo-local seed format:

```text
snapshots/examples/static_snapshot_v0/
  README_FIRST.txt
  index.html
  index.txt
  SNAPSHOT_MANIFEST.json
  BUILD_MANIFEST.json
  SOURCE_SUMMARY.json
  EVAL_SUMMARY.json
  ROUTE_SUMMARY.json
  PAGE_REGISTRY.json
  CHECKSUMS.SHA256
  SIGNATURES.README.txt
  data/README.txt
```

The seed snapshot is not part of the current `public_site/` artifact, is not a
production signed release, contains no real signing keys, contains no
executable downloads, and does not make `/snapshots/` an implemented public
route.

Relay Surface Design v0 adds no static export tree. It only records
`control/inventory/publication/relay_surface.json`, reference docs, an unsigned
operator checklist, and validation for future local/LAN relay work. Static
exports still contain no relay runtime, protocol server, network listener,
private-data exposure, live-probe passthrough, or write/admin route.

Expected future static data areas:

- `data/` for schema-versioned public JSON
- `snapshots/` for offline static bundles
- `data/build_manifest.json` for build provenance
- production signed snapshot manifests/checksums later, after key-management
  and release-signing policy exists

Static exports must remain portable between `/eureka/` and `/`.

Custom Domain / Alternate Host Readiness v0 adds host-portability validation
and policy records for future custom-domain or alternate-static-host work. It
does not add `public_site/CNAME`, DNS records, provider config, backend
hosting, live probes, or an alternate deployed artifact.

Live Backend Handoff Contract v0 adds no files under `/api/` and no route
handlers. It only records future `/api/v1` reservations and disabled
capability flags in publication inventory and generated static data summaries.
Static exports must continue to work with no backend at all.

Live Probe Gateway Contract v0 adds no source adapters and no network behavior.
It only records disabled future source-probe policy in publication inventory and
generated static data summaries. Static exports must not fetch URLs, call
Internet Archive or other external services, enable downloads, or imply live
probe availability.

Compatibility Surface Strategy v0 records the cross-surface contract for the
current static site, `/data/`, `/lite/`, `/text/`, `/files/`, `/demo/`, future
`/app/`, future `/web/`, future `/api/v1/`, future `/snapshots/`, future relay,
CLI, and future native clients. Signed Snapshot Format v0 adds only a
repo-local seed example and contract. Relay Surface Design v0 adds only
future-relay policy and validation. The current export still does not include
public snapshot bundles, production signatures, relay services, protocol
bridges, native apps, live API routes, live probes, or new runtime behavior.
