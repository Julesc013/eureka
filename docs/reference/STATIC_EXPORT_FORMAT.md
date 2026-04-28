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
surfaces, not live search, executable downloads, signed snapshots, relay
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

Expected future static data areas:

- `data/` for schema-versioned public JSON
- `snapshots/` for offline static bundles
- `data/build_manifest.json` for build provenance
- signed snapshot manifests/checksums later, after a snapshot slice exists

Static exports must remain portable between `/eureka/` and `/`.
