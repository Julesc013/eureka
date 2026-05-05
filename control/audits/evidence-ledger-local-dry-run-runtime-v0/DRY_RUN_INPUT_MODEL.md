# Dry-Run Input Model

Allowed inputs:

- Approved repo-local evidence-ledger candidate JSON files.
- Explicit `--example-root` values under `examples/evidence_ledger/`.
- `--all-examples`, which reads `examples/evidence_ledger/dry_run/`.
- Synthetic records created in unit tests under temporary directories.

Forbidden inputs:

- Arbitrary local paths outside approved example roots.
- Absolute private paths.
- URLs or source URL selectors.
- Live source identifiers.
- Connector parameters.
- Database paths.
- Cache roots.
- Uploaded files.
- Credentials.

The CLI rejects `--url`, `--live-source`, `--source-url`, `--connector`,
`--store-root`, `--index-path`, `--database`, `--write-authoritative`,
`--mutate`, `--publish`, `--promote`, `--accept-truth`, and
`--accept-evidence`.
