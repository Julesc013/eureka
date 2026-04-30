# Pack Validation

Pack validation is Eureka's validate-only workflow for governed source,
evidence, index, contribution, and master-index review queue examples.

It is not import. It does not implement import. It does not stage packs. It
does not mutate local indexes. It does not upload or submit packs. It does not mutate the master index.
It does not moderate submissions, fetch URLs, scrape sources, crawl, load
plugins, run downloads, or execute artifacts.

## Individual Validators

Existing pack validators remain the source of pack-specific checks:

```bash
python scripts/validate_source_pack.py
python scripts/validate_evidence_pack.py
python scripts/validate_index_pack.py
python scripts/validate_contribution_pack.py
python scripts/validate_master_index_review_queue.py
```

Each validator checks its own manifest shape, checksums, JSON/JSONL files,
privacy/status posture, rights/access docs, private-path and credential
guards, prohibited payloads, and contract-specific safety rules.

## Aggregate Validator

Pack Import Validator Aggregator v0 adds one validate-only command:

```bash
python scripts/validate_pack_set.py --list-examples
python scripts/validate_pack_set.py --all-examples
python scripts/validate_pack_set.py --all-examples --json
```

With no `--pack-root`, the command validates all known repo example packs from
`control/inventory/packs/example_packs.json`.

Validate one explicit pack root:

```bash
python scripts/validate_pack_set.py --pack-root examples/source_packs/minimal_recorded_source_pack_v0
python scripts/validate_pack_set.py --pack-root examples/evidence_packs/minimal_evidence_pack_v0 --json
```

The aggregate validator detects pack type from the root manifest:

- `SOURCE_PACK.json` => `source_pack`
- `EVIDENCE_PACK.json` => `evidence_pack`
- `INDEX_PACK.json` => `index_pack`
- `CONTRIBUTION_PACK.json` => `contribution_pack`
- `REVIEW_QUEUE_MANIFEST.json` => `master_index_review_queue`

You may pass `--pack-type` for an explicit root, but the command rejects a
mismatch between requested type and detected manifest.

## Known Example Roots

- `examples/source_packs/minimal_recorded_source_pack_v0`
- `examples/evidence_packs/minimal_evidence_pack_v0`
- `examples/index_packs/minimal_index_pack_v0`
- `examples/contribution_packs/minimal_contribution_pack_v0`
- `examples/master_index_review_queue/minimal_review_queue_v0`

## JSON Output

`--json` emits:

- `ok`
- `schema_version`
- `validator_id`
- `mode`
- `strict`
- `pack_results`
- per-pack `pack_root`, `pack_type`, `validator_command`, `status`,
  `exit_code`, `stdout_excerpt`, and `stderr_excerpt`
- summary counts for `passed`, `failed`, `unavailable`, `unknown_type`, and
  `total`
- `mutation_performed: false`
- `import_performed: false`
- `staging_performed: false`
- `indexing_performed: false`
- `network_performed: false`

## What Success Means

Successful validation means the pack or queue example passed its governed
structural, checksum, privacy, rights/access, and prohibited-content checks.

Validation success is not import, staging, indexing, upload, submission,
master-index acceptance, rights clearance, malware safety, canonical truth, or
production readiness.

Successful validation does not prove:

- canonical truth
- rights clearance
- malware safety
- compatibility truth
- source trust
- public-search eligibility
- master-index acceptance
- production readiness

## Future Import Pipeline

The aggregate validator is the first safe command before any future
validate-only import tool. Pack Import Report Format v0 now defines the durable
report envelope for recording aggregate validation outcomes:

```bash
python scripts/validate_pack_import_report.py --all-examples
python scripts/validate_pack_import_report.py --all-examples --json
```

The report format records validation results, issues, privacy/rights/risk
status, provenance, next actions, and hard mutation-safety fields. It does not
implement import. It does not stage packs. It does not mutate local index
state, runtime state, or public search. It does not mutate the master index. It
does not upload or submit anything.
It does not mutate local index state.
It does not mutate the master index.

Validate-Only Pack Import Tool v0 is implemented as the first report-producing
preflight:

```bash
python scripts/validate_only_pack_import.py --list-examples
python scripts/validate_only_pack_import.py --all-examples --json
```

It emits Pack Import Report v0 JSON for explicit roots or known examples. It
does not import, does not stage, does not index, does not upload, and does not
mutate runtime state, local indexes, public search, or the master index.
Actual staging, local index candidate handling, contribution queue export,
hosted submission, and master-index review remain separate future milestones.

AI Provider Contract v0 is validated separately with
`python scripts/validate_ai_provider_contract.py`. AI providers are not source,
evidence, index, contribution, or review-queue packs. AI outputs may later help
draft candidates only as typed, review-required suggestions; validation is not
truth, rights clearance, malware safety, or acceptance.
