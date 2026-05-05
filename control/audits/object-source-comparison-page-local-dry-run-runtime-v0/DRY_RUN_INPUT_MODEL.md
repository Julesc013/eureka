# Dry-Run Input Model

Supported inputs:

- Approved repo-local object page example JSON files under `examples/object_pages`.
- Approved repo-local source page example JSON files under `examples/source_pages`.
- Approved repo-local comparison page example JSON files under `examples/comparison_pages`.
- Approved repo-local page dry-run examples under `examples/page_runtime_dry_run`.
- Explicit `--example-root` values under those approved roots.
- `--all-examples` mode.
- Synthetic test records created under temporary test roots.

Forbidden inputs:

- Arbitrary local paths outside approved example roots.
- Private absolute paths.
- URLs.
- Live source identifiers.
- Connector parameters.
- Source-cache paths.
- Evidence-ledger paths.
- Database paths.
- Cache roots.
- Uploaded files.
- Credentials.

The CLI rejects `--url`, `--live-source`, `--source-url`, `--connector`,
`--source-cache-path`, `--evidence-ledger-path`, `--candidate-path`,
`--store-root`, `--index-path`, `--database`, `--serve`, `--route`, `--hosted`,
`--write-public`, `--mutate`, `--publish`, `--promote`, `--download`,
`--install`, and `--execute`.
