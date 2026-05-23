# Dry-Run Input Model

Supported inputs:

- approved repo-local example source-cache candidate JSON files
- explicit `--example-root` paths under `examples/sources/cache/dry_run`
- `--all-examples` for `examples/sources/cache/dry_run/dry_run`
- synthetic test records created in unit tests

Forbidden inputs:

- arbitrary local paths outside approved examples, except isolated temporary test roots
- absolute private paths
- URLs
- live source identifiers
- connector parameters
- database paths
- cache root parameters
- uploaded files
- credentials

The CLI rejects `--url`, `--live-source`, `--source-url`, `--connector`,
`--store-root`, `--index-path`, `--database`, `--write-authoritative`,
`--mutate`, `--publish`, and `--promote`.
