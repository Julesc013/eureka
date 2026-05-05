# Dry-Run Input Model

Supported inputs:

- approved repo-local source pack examples
- approved repo-local evidence pack examples
- approved repo-local index pack examples
- approved repo-local contribution pack examples
- approved repo-local pack import dry-run examples
- approved repo-local pack-set examples if present
- explicit `--example-root` values under approved repo example roots
- `--all-examples`
- synthetic test packs created in unit tests

Forbidden inputs include arbitrary local paths outside approved roots, absolute
private paths, path traversal, URLs, live source identifiers, connector params,
source-cache paths, evidence-ledger paths, database paths, cache roots,
uploaded files, credentials, and executable package or installer paths.

The CLI rejects `--url`, `--fetch-url`, `--live-source`, `--source-url`,
`--connector`, `--source-cache-path`, `--evidence-ledger-path`,
`--candidate-path`, `--quarantine-path`, `--staging-path`, `--store-root`,
`--index-path`, `--database`, `--serve`, `--upload`, `--admin`,
`--write-authoritative`, `--mutate`, `--publish`, `--promote`, `--execute`,
`--run-scripts`, and `--follow-urls`.
