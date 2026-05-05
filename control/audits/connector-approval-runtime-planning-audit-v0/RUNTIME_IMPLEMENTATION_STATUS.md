# Runtime Implementation Status

Inspection scope:

- `runtime/connectors/`
- `runtime/gateway/public_api/`
- public search route inventories
- connector validator and dry-run scripts
- source sync worker contracts

First-wave live metadata connector runtime status:

- `internet_archive_metadata`: planning_only; no live runtime implementation.
- `wayback_cdx_memento`: planning_only; no live runtime implementation.
- `github_releases`: implemented_local_dry_run for recorded fixture adapter only; no live GitHub API runtime.
- `pypi_metadata`: planning_only; no live runtime implementation.
- `npm_metadata`: planning_only; no live runtime implementation.
- `software_heritage`: planning_only; no live runtime implementation.

Existing recorded/fixture connector modules are deterministic local fixtures and
are not public-search live fanout. No unexpected live connector integration was
found.
