# Evidence Ledger Local Dry-Run Runtime

P99 adds a local dry-run evidence-ledger candidate loader, classifier, and
report builder. It is not an authoritative evidence-ledger runtime and does not
write evidence-ledger state.

## Purpose

The dry-run proves that synthetic repo-local evidence candidates can be loaded,
structurally checked, classified, and summarized without mutation. It gives
future source-cache and connector work a safe evidence target shape without
enabling connectors or public-search evidence reads.

## Local Dry-Run Scope

Implemented:

- Local candidate discovery under approved examples.
- Candidate JSON loading.
- Classification by evidence kind, claim kind, source family, provenance,
  review, privacy, public-safety, rights/risk, and promotion readiness.
- Deterministic JSON report generation.
- CLI and report validator.

Not implemented:

- Live source calls.
- Connector runtime.
- Source-sync worker execution.
- Authoritative evidence-ledger storage.
- Source cache writes.
- Candidate/public/local/master index mutation.
- Public search integration.
- Hosted runtime.
- Telemetry, accounts, uploads, downloads, installs, or execution.

## Approved Input Model

Allowed inputs are `examples/evidence_ledger/dry_run/`, explicit
`--example-root` paths under `examples/evidence_ledger/`, and temporary
synthetic records in tests.

Forbidden inputs include arbitrary local paths, URLs, live source selectors,
connector parameters, database paths, cache roots, uploaded files, and
credentials. The CLI rejects `--url`, `--live-source`, `--source-url`,
`--connector`, `--store-root`, `--index-path`, `--database`,
`--write-authoritative`, `--mutate`, `--publish`, `--promote`,
`--accept-truth`, and `--accept-evidence`.

## Output Report Model

The report contains candidate counts, candidate summaries, evidence kind counts,
claim kind counts, source family counts, provenance/review/privacy/public
safety/rights-risk/promotion counts, mutation summary, warnings, errors, and
hard booleans.

`local_dry_run` is true. Live source, external call, connector runtime,
source-sync worker, authoritative write, mutation, public-search mutation,
truth acceptance, promotion, telemetry, credential, download, install, and
execution fields are false.

## Classification Model

Evidence candidates are classified conservatively:

- Evidence kinds include source metadata, availability, capture presence,
  release metadata, package metadata, scoped absence, conflict, and unknown.
- Claim kinds include metadata, availability, version, source presence, scoped
  absence, conflict, and unknown.
- Source families include Internet Archive, Wayback/CDX/Memento, GitHub
  Releases, PyPI, npm, Software Heritage, local fixture, and unknown.
- Review and promotion readiness stay review-gated unless a future milestone
  accepts a separate policy.

## Claim Scope And Truth Boundary

The dry-run does not accept claims as truth. Scoped absence is not global
absence. Source presence is not safety. Metadata presence is not rights
clearance. Release/package presence is not installability. Compatibility
evidence is not compatibility truth.

## Provenance And Source Attribution Checks

Candidates must carry source and provenance context or they are rejected or
classified as insufficient/unknown. The dry-run does not approve sources or
prove source trust.

## Privacy And Public-Safety Checks

Policy checks reject private paths, URL-like values, secret-looking keys,
tokens, private identifiers, and unsafe local path patterns. Examples are
synthetic and public-safe.

## Rights, Risk, And Action Checks

The dry-run makes no rights clearance, malware safety, dependency safety, or
installability proof. It enables no download, install, execute, package-manager,
emulator, or VM action.

## Source Cache Boundary

Synthetic evidence candidates may reference source-cache candidates or future
source-cache refs. The dry-run does not read authoritative source cache, write
source cache, or treat source cache as truth.

## Candidate, Public, And Master Boundary

The dry-run does not create candidates, promote candidates, rebuild public
index, or mutate local/runtime/master indexes. It reports potential evidence
effect classes only.

## Connector Runtime Boundary

The dry-run does not execute connector runtimes or call live sources. Future
connector runtime work remains approval-gated.

Boundary summary: no live source calls.

The dry-run does not call live sources.

## Public Search Boundary

Public search does not read this dry-run runtime, does not call
evidence-ledger dry-run, and does not alter public search ordering or contents.
Future public-search evidence reads require separate approval.

Boundary summary: no public search integration.

## CLI Usage

```bash
python scripts/run_evidence_ledger_dry_run.py --all-examples --json
```

Optional:

```bash
python scripts/run_evidence_ledger_dry_run.py --example-root examples/evidence_ledger/dry_run --strict --json
```

## Validator Usage

```bash
python scripts/validate_evidence_ledger_dry_run_report.py
python scripts/validate_evidence_ledger_dry_run_report.py --json
```

## Examples

Synthetic examples cover source metadata, availability, release metadata,
package metadata, capture presence, conflicting claims, and scoped absence.

## Limitations

P99 is a local dry-run only. Authoritative ledger storage, source-cache reads,
connector runtimes, public-search evidence reads, truth acceptance, and
promotion decisions remain future gated work.

## Next Steps

Recommended next branch: `P100 - Public Search Runtime Integration Audit v0`.

Human/operator parallel: deploy hosted wrapper, configure backend URL, configure
edge/rate limits, verify static site, execute Manual Observation Batch 0, and
review evidence-ledger authoritative storage and review policy.
