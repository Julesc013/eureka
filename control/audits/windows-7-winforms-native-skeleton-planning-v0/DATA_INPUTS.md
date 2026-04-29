# Data Inputs

Allowed future inputs:

- `public_site/data/site_manifest.json`
- `public_site/data/source_summary.json`
- `public_site/data/eval_summary.json`
- `public_site/data/route_summary.json`
- `public_site/data/page_registry.json`
- `public_site/data/build_manifest.json`
- `public_site/demo/data/demo_snapshots.json`
- `snapshots/examples/static_snapshot_v0/README_FIRST.txt`
- `snapshots/examples/static_snapshot_v0/SNAPSHOT_MANIFEST.json`
- `snapshots/examples/static_snapshot_v0/BUILD_MANIFEST.json`
- `snapshots/examples/static_snapshot_v0/SOURCE_SUMMARY.json`
- `snapshots/examples/static_snapshot_v0/EVAL_SUMMARY.json`
- `snapshots/examples/static_snapshot_v0/ROUTE_SUMMARY.json`
- `snapshots/examples/static_snapshot_v0/PAGE_REGISTRY.json`
- `snapshots/examples/static_snapshot_v0/CHECKSUMS.SHA256`
- `snapshots/examples/static_snapshot_v0/SIGNATURES.README.txt`

Input rules:

- Use explicit relative paths only.
- No arbitrary local filesystem scanning.
- No private user paths.
- No secret or credential files.
- No executable/software artifacts.
- No network retrieval.
- No live backend or live probe input.
- Missing optional files must show a disabled/limited state rather than
  silently widening scope.

