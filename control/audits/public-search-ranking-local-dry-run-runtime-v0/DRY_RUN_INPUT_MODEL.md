# Dry-Run Input Model

Allowed inputs:

- Approved repo-local ranking dry-run examples.
- Approved repo-local public index or result fixtures when explicitly added to approved roots.
- Explicit `--example-root` paths under approved repo example roots.
- Optional `--all-examples` mode.
- Synthetic records created inside unit tests.

Current approved roots:

- `examples/public_search_ranking_dry_run`
- `examples/evidence_weighted_ranking`
- `examples/compatibility_aware_ranking`

Forbidden inputs:

- Arbitrary local paths outside approved roots.
- Absolute private paths.
- URLs or live source identifiers.
- Connector parameters.
- Source cache, evidence ledger, candidate, index, store, or database paths.
- Raw query observation logs.
- Telemetry, user profile, popularity, or ad signals.
- Uploaded files or credentials.

Rejected CLI fields include `--url`, `--live-source`, `--source-url`, `--connector`, `--source-cache-path`, `--evidence-ledger-path`, `--candidate-path`, `--store-root`, `--index-path`, `--database`, `--serve`, `--hosted`, `--write-public`, `--mutate`, `--publish`, `--promote`, `--suppress`, `--telemetry`, `--user-profile`, `--ad-signal`, `--model-provider`, and `--ai-rerank`.

