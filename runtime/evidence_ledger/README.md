# Evidence Ledger Local Dry-Run Runtime

This package implements the P99 local dry-run evidence-ledger candidate loader,
classifier, and deterministic report builder.

It is not an authoritative evidence-ledger runtime. It does not call live
sources, execute connector runtimes, write evidence-ledger state, mutate source
cache or indexes, accept claims as truth, create promotion decisions, or alter
public search.

Allowed inputs are repo-local synthetic examples under
`examples/evidence_ledger/dry_run/` or explicit approved example roots. Unit
tests may use temporary synthetic records. The package is stdlib-only and writes
no files; the CLI may write a dry-run report only to approved report paths.
