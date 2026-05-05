# Pack Import Local Dry-Run Runtime

P104 adds a local dry-run pack import runtime. It discovers approved repo-local
source, evidence, index, contribution, and dry-run pack-set examples, classifies
candidate effects, optionally invokes bounded repo validators, and emits a
deterministic report.

It is not authoritative import. It does not stage or quarantine real packs,
write source cache, write evidence ledger, mutate candidate/public/local/master
indexes, execute pack contents, follow URLs, create promotion decisions, expose
upload/admin endpoints, enable public contribution intake, or deploy anything.

## Approved Input Model

Use:

```bash
python scripts/run_pack_import_dry_run.py --all-examples --json
python scripts/run_pack_import_dry_run.py --all-examples --no-validator-commands --json
```

Explicit `--example-root` values must be under approved repo example roots:
`examples/source_packs`, `examples/evidence_packs`, `examples/index_packs`,
`examples/contribution_packs`, `examples/packs` if present, or
`examples/pack_import_dry_run`.

## Output Report Model

Reports include pack counts, summaries, schema versions, validation status,
privacy/public-safety/risk counts, mutation-impact counts, promotion-readiness
counts, dry-run candidate effects, mutation summary, warnings, errors, and hard
booleans.

## Classification Model

Pack candidates are classified by pack kind, schema version, validation status,
privacy status, public safety status, risk status, mutation impact, and
promotion readiness. Classification is not truth acceptance.

## Validation Pipeline

The dry-run may invoke existing repo-local validators for real source,
evidence, index, and contribution pack examples. It does not invoke external
commands, shell execution, network calls, import, staging, upload, or mutation.
Synthetic P104 dry-run inputs are classified directly.

## Import Report And Diff Model

Dry-run reports summarize candidate effects only. No authoritative stores are
read or compared unless a future milestone approves that boundary. No accepted
records or promotion decisions are created.

## Pack Handling

Source packs map to source-cache/source-inventory candidate effects. Evidence
packs map to evidence-ledger candidate effects. Index packs are compare-only
future inputs. Contribution packs remain review-required. Pack sets record
synthetic dependency relationships only.

## Quarantine And Staging Boundary

No real quarantine or staging store is created. P104 does not copy arbitrary
packs, write staging manifests, or call staged-pack inspection except through
separate existing validators when explicitly run by verification.

## Privacy, Path, Secret, Execution, And URL Policy

The dry-run rejects private paths, path traversal, credentials, tokens, private
identifiers, executable/run-script claims, mutation claims, promotion claims,
and URL fetch attempts. URL references, if ever allowed by a future contract,
are metadata only and must not be fetched by P104.

## Rights, Risk, Provenance, Mutation, And Contribution Boundaries

Pack claims are not truth. License metadata is not rights clearance. Malware
safety is not claimed. Source/evidence provenance must be preserved. Public
contribution intake requires a separate runtime, abuse policy, storage policy,
privacy policy, review workflow, and operator approval.

## Validator

```bash
python scripts/validate_pack_import_dry_run_report.py
python scripts/validate_pack_import_dry_run_report.py --json
```

The validator checks the audit pack, report JSON, required fields, hard
booleans, count consistency, and no import/staging/quarantine/promotion/
execution/fetch/upload/admin/mutation claims.

## Limitations And Next Steps

This is local dry-run evidence only. Next recommended branch is P105 Deep
Extraction Runtime Planning v0 only after sandbox policy approval.
