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

Expected future static data areas:

- `data/` for schema-versioned public JSON
- `files/` for text manifests and checksums
- `snapshots/` for offline static bundles
- `data/build_manifest.json` for build provenance
- checksum files later, after a checksum-producing slice exists

Static exports must remain portable between `/eureka/` and `/`.
