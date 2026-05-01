# Local Staging Manifest Format

Local Staging Manifest Format v0 defines the future local/private manifest a
local quarantine or staging tool may write after a validate-only import report
is reviewed and a user or operator explicitly chooses future staging.

It is contract, example, and validation only. No staging runtime exists. This
format does not create staged state, does not copy pack contents, does not
import source/evidence/index/contribution packs, does not mutate public search,
does not mutate a local index, does not mutate the runtime source registry, and
does not mutate the master index.

## Purpose

A local staging manifest records:

- which validate-only import report authorized the future staging action
- which pack references are in local quarantine
- which staged entities are present as local candidates
- staged entity counts
- privacy, rights, risk, checksum, and provenance summaries
- hard no-mutation guarantees
- future reset, delete, inspect, and export policy
- limitations and non-goals

Manifest validity is not canonical truth, rights clearance, malware safety,
source trust, public-search eligibility, local index eligibility, or
master-index acceptance.

## Lifecycle

The safe future flow is:

1. Run validate-only pack import.
2. Review Pack Import Report v0.
3. Explicitly choose a future local staging action.
4. A future tool writes a local/private staging manifest under an allowed,
   ignored local root.
5. A future staged pack inspector reads the manifest and reports candidates.
6. Delete, reset, or export report-only views remain available.

P47 implements only the manifest format, synthetic example, validator, docs,
and audit pack. It does not implement step 4 as runtime behavior.

## Required Fields

`contracts/packs/local_staging_manifest.v0.json` requires:

- `schema_version: local_staging_manifest.v0`
- `manifest_id`
- `manifest_version`
- `manifest_kind: local_staging_manifest`
- `status`
- `created_by_tool`
- `staging_mode`
- `source_validate_report_ref`
- `staged_pack_refs`
- `staged_entities`
- `counts`
- `privacy_rights_risk_summary`
- `provenance_summary`
- `no_mutation_guarantees`
- `reset_delete_export_policy`
- hard no-mutation fields
- `limitations`
- `notes`

Allowed statuses include `planned_example`, `local_private`,
`staged_quarantine`, `inspectable`, `delete_requested`, `reset_requested`,
`exported_report_only`, and `superseded`.

## Validate Report Reference

`source_validate_report_ref` links the manifest to the reviewed Pack Import
Report v0. It records the report ID, path policy, optional checksum, report
status, producing tool, and limitations.

Committed examples must not contain real local absolute paths. They use
`example_committed` or redacted path policy. Future local/private manifests may
use explicit local paths only under local-private classification and only in
ignored user-controlled roots.

## Staged Pack References

Each `staged_pack_refs` entry records:

- staged pack reference ID
- pack ID and version
- pack type
- pack checksum
- pack root policy
- validation status
- privacy, rights, and risk classifications
- limitations

Supported pack types are source, evidence, index, contribution, master-index
review queue, and AI output bundle references. A staged pack reference is not
an import and not an acceptance decision.

## Staged Entities

`staged_entities` are local candidates only. Supported entity types are:

- `staged_source_candidate`
- `staged_evidence_candidate`
- `staged_index_summary`
- `staged_contribution_candidate`
- `staged_ai_output_candidate`
- `staged_issue`
- `staged_decision_note`

Each entity records optional pack refs, optional subject refs, public-safe
posture, privacy/rights/risk classifications, review status, summary,
limitations, and provenance refs.

Allowed review statuses are `unreviewed`, `validated_structure`,
`quarantine_required`, `inspectable_local`,
`local_index_candidate_future`, `contribution_candidate_future`, and
`rejected_local`. None of these statuses accept the entity as canonical.

## Counts

The manifest records counts for staged packs, staged entities, each candidate
class, issues, blocked issues, private records, and public-safe records. The
validator checks the committed example counts against the staged entities.

## No-Mutation Guarantees

The top level and `no_mutation_guarantees` both require:

- `public_search_mutated: false`
- `local_index_mutated: false`
- `canonical_source_registry_mutated: false`
- `runtime_state_mutated: false`
- `master_index_mutated: false`
- `upload_performed: false`
- `live_network_performed: false`

The validator rejects manifests that claim public search, local index, runtime
source registry, upload, network, or master index mutation.

## Reset, Delete, And Export

`reset_delete_export_policy` prepares future tooling by requiring:

- future delete-one-staged-pack support
- future clear-all-staged-state support
- future manifest export support
- future public-safe report export support
- `export_private_data_default: false`
- future confirmation for irreversible deletes

This is policy only. No delete, reset, export, staging, or inspector runtime is
implemented by this milestone.

## Privacy, Rights, And Risk

Local staging is local/private by default. Public-safe candidate records still
remain candidates. Rights uncertainty remains review-required. The manifest
must not contain credentials, API keys, secrets, private keys, unredacted
private absolute paths, executable payloads, raw databases, raw caches, or raw
private files.

The manifest must not claim rights clearance, malware safety, canonical truth,
source trust finality, local index acceptance, public search acceptance, or
master-index acceptance.

## Relationships

Validate-Only Pack Import Tool v0 produces Pack Import Report v0 and does not
stage. Pack Import Report Format v0 records validation outcomes. Local
Quarantine/Staging Model v0 defines private-by-default staging posture.
Staging Report Path Contract v0 defines stdout defaults, explicit output paths,
forbidden roots, ignored local roots, and redaction.

Local Staging Manifest Format v0 sits after those contracts and before Staged
Pack Inspector v0. The future inspector should read manifests, report staged
candidate posture, and still avoid public search, local index, runtime source
registry, relay, snapshot, upload, or master-index mutation.

Native clients may later display local/private staging manifests from
application-local data roots. Relay must not expose staged data by default.
Snapshots must exclude local/private staging manifests by default. Typed AI
outputs may appear only as typed, review-required staged AI output candidates.

## Validation

Validate all example manifests:

```bash
python scripts/validate_local_staging_manifest.py
python scripts/validate_local_staging_manifest.py --json
python scripts/validate_local_staging_manifest.py --all-examples
python scripts/validate_local_staging_manifest.py --all-examples --json
```

Validate one manifest root:

```bash
python scripts/validate_local_staging_manifest.py --manifest-root examples/local_staging_manifests/minimal_local_staging_manifest_v0 --strict
```

The validator is stdlib-only and offline. It performs no model calls, network
calls, staging, import, index mutation, upload, runtime mutation, or
master-index mutation.

## Deferred

Still future: Staged Pack Inspector v0, local staging tool, runtime staging
directories, staged delete/reset tooling, local index candidate planning,
contribution queue export, native staging UI, hosted submission, rights
clearance, malware safety review, production readiness, and any master-index
acceptance path.
