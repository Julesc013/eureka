# Public Search Boundary Status

Public search must not call connectors live.

Current boundary:

- Public search live connector fanout: disabled.
- Public search connector/live/source URL parameters: forbidden by public search safety policy.
- Public search reads reviewed public/local index artifacts only.
- Source-cache and evidence-ledger dry-runs are not public-search runtimes.
- Static site must not claim live connector coverage.

Future public search may read reviewed public index or reviewed public-safe
source-cache summaries only after separate approval. Public-query-triggered
external source fanout remains forbidden.
