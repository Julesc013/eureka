# Contribution Pack Contract

Contribution Pack Contract v0 defines a portable, validated review-submission
wrapper. It lets future users, maintainers, archivists, and clients package
candidate improvements without giving Eureka upload authority, import authority,
private-cache access, executable plugin authority, live network access, or
master-index acceptance.

This contract is validation and governance only. It does not implement
contribution upload, source/evidence/index pack import, moderation UI, accounts,
identity, master-index review queue runtime, live connectors, downloads,
installers, executable plugins, automatic acceptance, or production extension
support.

## Pack Layout

Required files:

- `CONTRIBUTION_PACK.json`
- `README.md`
- `PRIVACY_AND_RIGHTS.md`
- `CHECKSUMS.SHA256`
- `contribution_items.jsonl`

Optional files:

- `source_pack_refs.jsonl`
- `evidence_pack_refs.jsonl`
- `index_pack_refs.jsonl`
- `manual_observations.jsonl`
- `metadata_corrections.jsonl`
- `alias_suggestions.jsonl`
- `compatibility_suggestions.jsonl`
- `member_path_suggestions.jsonl`
- `absence_reports.jsonl`
- `result_feedback.jsonl`
- `review_notes.jsonl`
- `manifests/`
- `tests/`
- `licenses/`
- `references/`

The manifest schema is `contracts/packs/contribution_pack.v0.json`.

## Manifest

`CONTRIBUTION_PACK.json` declares `schema_version`, `pack_id`,
`pack_version`, `title`, `description`, `status`, `producer`,
`contribution_scope`, `contribution_item_files`, `referenced_packs`, `privacy`,
`rights_and_access`, `review_requirements`, `checksum_policy`, `validation`,
`prohibited_contents`, and `notes`.

Lifecycle statuses follow Pack Lifecycle guidance: `draft`, `local_private`,
`validated_local`, `shareable_candidate`, `submitted`, `quarantined`,
`review_required`, `accepted_public`, `rejected`, and `superseded`. A status is
not acceptance by itself. `accepted_public` requires a future governed review
path; P37 does not create that path.

## Contribution Items

`contribution_items.jsonl` contains review-candidate records. Each record should
include:

- `contribution_id`
- `contribution_type`
- optional `target_ref`
- optional `subject_ref`
- optional `source_ref`
- optional `pack_ref`
- `summary`
- `proposed_action`
- `evidence_refs`
- optional `confidence`
- `privacy_classification`
- `rights_classification`
- `review_status`
- `limitations`
- `created_by_pack`

Allowed contribution types are `source_record_candidate`,
`evidence_record_candidate`, `index_coverage_candidate`, `manual_observation`,
`metadata_correction`, `alias_suggestion`, `compatibility_suggestion`,
`member_path_suggestion`, `checksum_observation`, `absence_report`,
`dead_link_report`, `result_quality_feedback`, `source_coverage_report`,
`duplicate_or_identity_candidate`, `documentation_hint`, and `review_note`.

Contribution items are review candidates, not truth. They are proposals for
review, not automatic mutations and not canonical truth.

## Proposed Actions

Allowed proposed actions are `add_candidate`, `update_candidate`,
`deprecate_candidate`, `mark_review_required`, `link_existing_records`,
`split_identity_candidate`, `merge_identity_candidate_for_review`,
`add_absence_evidence`, `add_compatibility_evidence`,
`add_member_path_evidence`, `add_alias_candidate`, and `no_action_note`.

A proposed action is a request for review. It must not directly change source
registries, public search results, snapshots, hosted indexes, or a future master
index.

## Referenced Packs

Contribution packs may reference source, evidence, and index packs through
JSONL reference files. A reference record includes `pack_ref`, `pack_type`,
`pack_id`, `pack_version`, optional `relative_path`, optional `checksum`,
`validation_status`, and `notes`.

References do not import or embed packs by default. They are review links that a
future review queue or local import planner can inspect after separate approval.

## Manual Observations

`manual_observations.jsonl` may carry observation placeholders or already
reviewed manual observations. Each observation includes `observation_id`,
`system_id`, `query_id`, optional `observed_at`, optional `operator`,
`observation_status`, `summary`, optional `result_refs`, and `notes`.

Do not mark Google, Internet Archive, or other external baseline observations as
observed unless a valid human-entered observation file exists. Pending
observations are allowed and remain non-evidence until reviewed.

## Privacy

Pack and item privacy classes are `public_safe`, `local_private`,
`review_required`, `restricted`, and `unknown`.

The safe authoring default is local-private. `shareable_candidate` and
`submitted` packs must not contain local-private records, credentials, private
absolute paths, private cache exports, raw databases, executable payloads,
restricted records, or unreviewed external observations. `accepted_public`
requires future review and must not contain review-required, restricted, or
local-private records.

## Rights And Access

Every contribution pack must include `PRIVACY_AND_RIGHTS.md`.

A contribution is not rights clearance, not malware safety, and not canonical
truth. It does not grant artifact distribution permission, download permission,
installer permission, or executable safety. Raw binaries, raw private files,
long copyrighted text, credentials, and private paths are forbidden by default.

Future hosted or master-index acceptance needs review, redaction, source/evidence
comparison, conflict handling, takedown posture, and operator approval.

## Checksums

`CHECKSUMS.SHA256` records SHA-256 checksums for pack files, excluding the
checksum file itself. Shareable and submitted packs must include checksums.
Production signing is future/deferred and is not implemented by this contract.

## Validation

Validate the example contribution pack:

```bash
python scripts/validate_contribution_pack.py
python scripts/validate_contribution_pack.py --json
python scripts/validate_contribution_pack.py --strict
```

The validator checks manifest fields, JSON and JSONL parsing, contribution id
uniqueness, contribution types, proposed actions, referenced pack records,
manual observation posture, privacy/status consistency, checksums,
privacy/rights docs, private paths, prohibited credential fields, raw database
or cache extensions, executable payload extensions, and no live network
behavior.

The validator does not upload, import, review, moderate, accept, execute, fetch,
scrape, crawl, or add records to a master index.

## Relationship To Other Packs

Source packs define source metadata plus optional fixture/evidence inputs.
Evidence packs carry claims and observations. Index packs describe index builds,
source coverage, field coverage, query examples, and public-safe record
summaries. Contribution packs wrap proposed changes and/or referenced packs so
they can later enter a governed review process.

Contribution packs do not replace source/evidence/index provenance and do not
make any referenced pack authoritative.

## Master Index Review Queue

Master Index Review Queue Contract v0 defines the future queue entries,
reviewer states, conflict handling, quarantine states, accepted public deltas,
rejection reasons, audit trails, and publication gates for contribution
candidates.

Contribution Pack Contract v0 only defines what a candidate submission bundle
looks like. Queue validation is not acceptance, and accepted_public remains
limited, review-governed, and evidence/provenance-bound.

## Runtime Consumers

Future public search, native clients, relay clients, snapshots, hosted search
rehearsals, and review tools may display or compare reviewed contribution-pack
summaries after separate implementation milestones. Current public search
remains local/prototype and `local_index_only`.

Source/Evidence/Index Pack Import Planning v0 treats contribution packs as
supported future validation inputs for local inspection and review-candidate
preparation. Validate-only must come before private quarantine, and private
quarantine must come before any local index candidate or review queue export.
Planning does not implement contribution import, upload, moderation, automatic
acceptance, public-search mutation, or master-index mutation.

## Not Implemented

Contribution Pack Contract v0 does not implement contribution upload, source
pack import, evidence pack import, index pack import, moderation UI, accounts,
identity, master-index review queue runtime, automatic acceptance, source
registry mutation, hosted ingestion, live source probes or live connectors,
arbitrary URL fetching, crawling or scraping, private cache sharing, raw SQLite
or cache export, executable plugin loading, downloads or installers, native
clients, relay runtime, snapshot reader runtime, production signing, malware
safety, rights clearance, or production readiness.
