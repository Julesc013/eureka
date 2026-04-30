# Pack Import Report Format v0

Pack Import Report Format v0 defines Pack Import Report v0, the durable report
that Validate-Only Pack Import Tool v0 emits after pack validation and before
any future staging or review action. It is format/validation/example-only.

It does not implement import. It does not stage packs. It does not mutate local
index state, runtime source registry state, or public search. It does not
mutate the master index. It does not upload, submit, moderate, call models,
call networks, fetch URLs, or accept pack records as truth.
It does not index.
It does not mutate local index state.
It does not mutate the master index.
Validate-Only Pack Import Tool v0 emits Pack Import Report v0 and does not import, does not stage, does not index, does not upload, and does not mutate the master index.
Local Quarantine/Staging Model v0 is planning-only. No staging runtime exists,
it does not create staged state, and it does not import, does not stage, does
not index, does not upload, and does not mutate public search or the master
index. Future staged metadata must link back to Pack Import Report v0.

## Purpose

A pack import report records:

- which source, evidence, index, contribution, review-queue, or typed AI output
  inputs were checked
- which validators ran
- which validations passed, failed, were unavailable, or had unknown type
- checksum, schema, privacy, rights, and risk posture
- issues such as private paths, credentials, executable payloads, raw database
  files, or unsupported features
- provenance such as input roots and validator commands
- hard mutation-safety fields proving that no import/staging/index/upload or
  master-index mutation occurred
- explicit next actions that are reviewable and future-gated

The report is evidence of validation activity. It is not evidence of import,
truth, rights clearance, malware safety, source trust, or master-index
acceptance.

## Lifecycle

Reports are produced after validation in the future safe flow:

1. User or operator selects a governed pack root or known example set.
2. Aggregate or individual validators run offline.
3. A report records outcomes, issues, provenance, and hard false mutation flags.
4. The operator chooses a safe next action.

The first mode is `validate_only`. Future modes are named but not implemented:
`stage_local_quarantine_future`, `inspect_staged_future`,
`local_index_candidate_future`, and `contribution_queue_candidate_future`.

## Statuses

`report_status` may be:

- `validate_only_passed`
- `validate_only_failed`
- `partial_validation`
- `unsupported_pack_type`
- `blocked_by_policy`
- `unavailable_validator`
- `future_import_not_performed`

`validate_only_passed` means all recorded pack results passed structure checks.
It does not mean pack records were imported or accepted.

## Pack Results

Each `pack_results` entry records:

- `pack_root`
- `pack_type`: `source_pack`, `evidence_pack`, `index_pack`,
  `contribution_pack`, `master_index_review_queue`, `ai_output_bundle`, or
  `unknown`
- optional `pack_id` and `pack_version`
- `validator_id` and optional `validator_command`
- `validation_status`: `passed`, `failed`, `unavailable`, `unknown_type`, or
  `skipped`
- checksum, schema, privacy, rights, and risk statuses
- issue count and issue records
- record counts
- limitations
- a recommended next action

Source packs, evidence packs, index packs, and contribution packs remain
distinct. Index-pack summaries are coverage records, not raw caches or
databases. Contribution packs remain review candidates. Review queues remain
future governance fixtures.

## Issue Model

Issues have severity `info`, `warning`, `error`, or `blocked`.

Issue types include schema and checksum errors, privacy failures, rights or
risk review requirements, executable payloads, raw databases, private paths,
credentials, unknown pack types, unavailable validators, unsupported features,
and policy blocks.

Blocked and error issues should include remediation. A private-path issue should
be redacted before a report is shareable.

## Privacy, Rights, And Risk

The report format records privacy, rights, and risk status. It does not clear
rights, prove malware safety, or decide canonical truth. Reports must not store
API keys, secrets, passwords, private keys, credentials, or unredacted private
absolute paths.

Uncertainty can be represented as `review_required`, `restricted`, `unknown`,
or `failed`. The safe next action is revalidation, local-private retention,
future quarantine, rejection, or future review, not silent import.

## Mutation Safety

Every report has hard safety fields:

- `import_performed: false`
- `staging_performed: false`
- `indexing_performed: false`
- `upload_performed: false`
- `master_index_mutation_performed: false`
- `runtime_mutation_performed: false`
- `network_performed: false`

The same fields appear inside `mutation_summary`. The v0 validator rejects
reports that claim any of these actions happened.

## Next Actions

Allowed next actions are:

- `no_action`
- `fix_pack_and_revalidate`
- `keep_local_private`
- `quarantine_future`
- `stage_local_quarantine_future`
- `inspect_future`
- `create_contribution_candidate_future`
- `submit_for_review_future`
- `reject`
- `unsupported`

No allowed action performs automatic import or acceptance.

## Examples

Synthetic example reports live under `examples/import_reports/`:

- `validate_only_all_examples.passed.json`
- `validate_only_private_path.failed.json`
- `validate_only_unknown_pack_type.failed.json`

The private-path example uses `<redacted-local-path>` and does not preserve a
real local path.

## Validation

Validate all example reports:

```bash
python scripts/validate_pack_import_report.py
python scripts/validate_pack_import_report.py --json
python scripts/validate_pack_import_report.py --all-examples
python scripts/validate_pack_import_report.py --all-examples --json
```

Validate one report:

```bash
python scripts/validate_pack_import_report.py --report examples/import_reports/validate_only_all_examples.passed.json
```

The validator is stdlib-only and offline. It validates report structure, allowed
statuses, issue types, next actions, hard false mutation fields, private path
redaction, absence of secrets, and absence of positive truth/rights/malware
authority claims.

## Relationships

Pack Import Validator Aggregator v0 validates packs. Pack Import Report Format
v0 records validation outcomes. Validate-Only Pack Import Tool v0 now combines
both by running validators and writing a report in this format without import,
staging, indexing, upload, runtime mutation, or master-index mutation.

Typed AI Output Validator v0 can validate typed AI output candidates. A pack
import report may record those validation results as `ai_output_bundle`, but it
does not accept AI output as evidence, contribution material, truth, rights
clearance, malware safety, or source trust.

Local search, native clients, relay, and snapshots are unaffected in v0.
Reviewed public records may later flow through contribution packs and the
Master Index Review Queue Contract v0, but this report format does not mutate
that queue or any hosted master index.

## Not Implemented

Pack Import Report Format v0 does not implement pack import runtime, staging,
quarantine directories, local index mutation, runtime source registry mutation,
public search mutation, source/evidence/index/contribution pack import,
master-index queue import, upload, submission, moderation UI, accounts,
identity, AI provider runtime, model calls, API keys, executable plugins, live
connectors, live probes, arbitrary URL fetching, crawling, downloads,
installers, native clients, relay runtime, snapshot reader runtime, rights
clearance, malware safety, canonical truth selection, or production readiness.
