# Existing Index Seams

- `runtime/local/search_index.py` already provides deterministic local search
  documents and result-card conversion.
- `runtime/local/local_search.py` owns the local search response shape and
  no-mutation flags.
- `scripts/eureka_index.py` is the existing index CLI surface.
- `scripts/eureka_search.py` is the existing local search CLI surface.
- `runtime/resolution_run/**` provides durable run bundles and lane snapshots.

The Preview Index reuses these seams instead of replacing them. It adds a new
`preview` index mode and keeps the existing `local` mode compatible.
