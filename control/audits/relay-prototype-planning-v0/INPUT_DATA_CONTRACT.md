# Input Data Contract

Allowed initial inputs for a future approved prototype:

- `public_site/data/*.json`
- `public_site/text/*`
- `public_site/files/*`
- `snapshots/examples/static_snapshot_v0/*`
- generated public data summaries
- static snapshot manifests and checksums

The future prototype should use allowlisted repo-relative roots only. It must
not scan for inputs.

Disallowed initial inputs:

- arbitrary user directories
- private cache roots
- credentials
- account data
- local browser history
- private search history
- unreviewed downloads
- live API responses
- live probe outputs
- external URLs
- local absolute paths supplied by a caller

Missing optional static inputs must produce explicit unavailable/unsupported
status later. They must not cause network fetches, crawling, scraping, or
arbitrary local filesystem ingestion.
