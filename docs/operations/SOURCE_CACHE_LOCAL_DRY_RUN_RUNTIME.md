# Source Cache Local Dry-Run Runtime

P98 adds a bounded local dry-run runtime for source-cache candidate examples. It
loads approved repo-local synthetic JSON files, validates their shape,
classifies their source family and policy posture, and emits deterministic
reports.

## Scope

Implemented:

- `runtime/source_cache/` dry-run modules
- `scripts/run_source_cache_dry_run.py`
- `scripts/validate_source_cache_dry_run_report.py`
- synthetic examples under `examples/source_cache/dry_run`

Not implemented:

- live source calls
- connector runtime
- source sync worker execution
- authoritative source-cache storage
- evidence ledger writes
- candidate/public/local/master index mutation
- public search integration
- hosted runtime
- telemetry, credentials, accounts, downloads, uploads, installs, or execution

No live source calls, no public search integration, and no authoritative
source-cache runtime behavior are added by this local dry-run lane.

## Approved Input Model

The normal input is `examples/source_cache/dry_run`. The CLI supports
`--all-examples` or an explicit `--example-root` under `examples/source_cache`.
Unit tests may use isolated temporary roots for synthetic negative checks.

The CLI rejects live-source and mutation-shaped parameters such as `--url`,
`--live-source`, `--source-url`, `--connector`, `--store-root`, `--index-path`,
`--database`, `--write-authoritative`, `--mutate`, `--publish`, and `--promote`.

## Output Report Model

Dry-run output is JSON with `mode: local_dry_run`, candidate counts,
classification summaries, mutation summary, warnings, errors, and hard
booleans. `local_dry_run` is true. Live calls, connector execution,
source-sync execution, authoritative writes, source/evidence/candidate/index
mutation, public-search mutation, telemetry, credentials, downloads, installs,
and execution remain false.

## Classification Model

Candidates are classified by source family, record kind, privacy status, public
safety status, evidence readiness, and policy status. Unknown or unsupported
required enum values make a candidate invalid in strict mode.

## Privacy And Public Safety

The dry-run rejects URL-like values, private paths, path traversal, secret-like
markers, credentials, IP addresses, account identifiers, and forbidden record
keys. Examples are synthetic and public-safe. No private data is published.

## Source Attribution

Each candidate must include source family and source reference metadata.
Source-policy posture is descriptive only; the dry-run does not approve a
connector, prove availability, or treat source-derived data as truth.

## Boundaries

Evidence ledger readiness is classification-only. No evidence-ledger records are
created. Candidate, public, local, runtime, and master indexes are not mutated.
Connector runtimes do not run. Public search does not read this runtime and its
ordering and contents are unchanged.

## Usage

```bash
python scripts/run_source_cache_dry_run.py --all-examples --json
python scripts/validate_source_cache_dry_run_report.py
python scripts/validate_source_cache_dry_run_report.py --json
```

## Examples

The committed examples cover synthetic Internet Archive metadata, Wayback-style
capture metadata, GitHub Releases metadata, package metadata, and Software
Heritage identity metadata.

## Limitations

This is not authoritative source-cache runtime. It is a local dry-run candidate
reporter. Future authoritative storage requires a separate plan, approval,
mutation boundary, rollback model, and public-search integration review.
