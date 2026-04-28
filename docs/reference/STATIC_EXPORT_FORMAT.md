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
  assets/
```

`public_site/` is the active hand-authored static public artifact. It remains in
place for this milestone.

Future generated export:

```text
site/
  pages/
  templates/
  data/
  assets/
  build.py
site/dist/
  index.html
  data/
  files/
  snapshots/
```

The future shape is reserved only. This milestone does not create a generator,
Node/npm chain, frontend framework, or `site/` tree.

Expected future static data areas:

- `data/` for schema-versioned public JSON
- `files/` for text manifests and checksums
- `snapshots/` for offline static bundles
- `data/build_manifest.json` for build provenance
- checksum files later, after a checksum-producing slice exists

Static exports must remain portable between `/eureka/` and `/`.

