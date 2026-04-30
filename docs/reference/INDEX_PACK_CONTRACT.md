# Index Pack Contract

Index Pack Contract v0 defines a portable, validated bundle of public-safe index
coverage metadata. It lets future users, maintainers, native clients, relay
clients, snapshots, hosted search rehearsals, and review workflows understand
what an index build covered without sharing a raw local cache, a SQLite
database, private paths, raw source payloads, executable artifacts, or a
production search database.

This contract is validation and governance only. It does not implement index
pack import, merge, uploads, hosted submission, live connectors, raw database
export, executable plugins, master-index acceptance, or canonical truth
selection.

## Pack Layout

Required files:

- `INDEX_PACK.json`
- `README.md`
- `PRIVACY_AND_RIGHTS.md`
- `CHECKSUMS.SHA256`
- `index_summary.json`
- `source_coverage.json`
- `record_summaries.jsonl`

Optional files:

- `field_coverage.json`
- `query_examples.jsonl`
- `evidence_references.jsonl`
- `source_references.jsonl`
- `compatibility_summary.json`
- `member_summary.json`
- `absent_or_gap_summary.json`
- `manifests/`
- `tests/`
- `licenses/`
- `references/`

The manifest schema is `contracts/packs/index_pack.v0.json`.

## Manifest

`INDEX_PACK.json` declares `schema_version`, `pack_id`, `pack_version`,
`title`, `description`, `status`, `producer`, `index_build`,
`source_inventory_reference`, `schema_versions`, `index_mode`, `privacy`,
`rights_and_access`, `files`, `checksum_policy`, `validation`,
`prohibited_contents`, and `notes`.

Lifecycle statuses follow Pack Lifecycle guidance: `draft`, `local_private`,
`validated_local`, `shareable_candidate`, `submitted`, `quarantined`,
`review_required`, `accepted_public`, `rejected`, and `superseded`. A lifecycle
status does not grant import, merge, upload, indexing, network, plugin, cache
export, artifact distribution, or master-index authority. `accepted_public`
requires a future governed review path; P36 does not create that path.

## Index Build

`index_build` describes the build without shipping the database. The v0 shape
includes `index_build_id`, `index_format`, `producer_tool`, optional
`producer_version`, optional `input_pack_refs`, `source_count`, `record_count`,
optional evidence/member/compatibility counts, optional generated artifact
references, `deterministic`, `private_data_included`, `raw_cache_included`, and
`database_included`.

The v0 public example uses `index_format: summary_only`,
`raw_cache_included: false`, and `database_included: false`.

## Index Summary

`index_summary.json` records the overall shape of the index build:

- `schema_version`
- `index_build_id`
- `index_mode`
- `record_count`
- `record_kind_counts`
- `source_count`
- `source_family_counts`
- `field_coverage_summary`
- `query_profile_summary`
- `limitations`
- `generated_from`
- `privacy_classification`

Record kinds align with current local-index and public-search concepts:
`source_record`, `resolved_object`, `state_or_release`, `representation`,
`member`, `synthetic_member`, `evidence`, `article_segment`, and `other`.

## Source Coverage

`source_coverage.json` lists indexed source coverage without exposing raw
caches. Each source entry includes `source_id`, `source_family`,
`coverage_depth`, `status`, `record_count`, optional evidence/member/
compatibility counts, `limitations`, and `public_safe`.

This file answers what source families and records were represented. It does
not register sources by itself and does not approve live connectors.

## Record Summaries

`record_summaries.jsonl` contains public-safe record summaries. Each record
summary includes `record_id`, `record_kind`, `title`, `source_id`,
`source_family`, optional `public_target_ref`, optional `representation_kind`,
optional `member_path`, optional `result_lane`, optional `user_cost`, optional
`compatibility_summary`, optional `evidence_count`, `public_safe`, and
`limitations`.

Record summaries are coverage metadata, not canonical proof. They must not
include private absolute paths, credentials, raw payloads, internal SQLite row
ids unless made public-safe, binary blobs, long copyrighted snippets, or
download/install URLs.

## Field Coverage

`field_coverage.json` can document `searchable_fields`, `indexed_fields`,
`display_fields`, `internal_fields_excluded`, `private_fields_excluded`, and
`stability_notes`. This gives future local, native, relay, hosted, and snapshot
consumers a bounded view of what fields are safe to rely on.

## Query Examples

`query_examples.jsonl` may include representative queries, expected behavior,
optional minimum result counts, result notes, and limitations. Query examples
are rehearsal hints only. They do not promise production ranking or relevance.

## Privacy

Pack and record privacy classes are `public_safe`, `local_private`,
`review_required`, `restricted`, and `unknown`.

The safe default while authoring is local-private. `shareable_candidate` and
`submitted` packs must not contain local-private records, credentials, private
absolute paths, private cache exports, raw databases, or restricted records.
`accepted_public` requires future review and must not contain review-required,
restricted, or local-private records.

## Rights And Access

Every index pack must include `PRIVACY_AND_RIGHTS.md`.

Index metadata is not rights clearance. Indexed existence does not imply
artifact distribution permission. Record summaries may reference sources but do
not grant download rights. Index packs do not include executables, installers,
raw private files, raw caches, raw SQLite databases, or raw copyrighted
long-form text by default. Future public or master-index acceptance requires a
separate review workflow.

## Checksums

`CHECKSUMS.SHA256` records SHA-256 checksums for pack files, excluding the
checksum file itself. Shareable and submitted packs must include checksums.
Production signing is future/deferred and is not implemented by this contract.

## Validation

Validate the example index pack:

```bash
python scripts/validate_index_pack.py
python scripts/validate_index_pack.py --json
python scripts/validate_index_pack.py --strict
```

The validator checks manifest fields, JSON and JSONL parsing, record id
uniqueness, source coverage references, record kinds, privacy/status
consistency, checksums, privacy/rights docs, private paths, prohibited
credential fields, raw database extensions, executable payload extensions, and
no live network behavior.

The validator does not import, merge, index, upload, execute, fetch, scrape,
export raw databases, or accept index records into a master index.

## Relationship To Other Packs

Source packs define source metadata plus optional fixture/evidence inputs.
Evidence packs carry claims and observations. Index packs describe an index
build, source coverage, field coverage, query examples, and public-safe record
summaries. Contribution packs wrap proposed changes and/or source, evidence, and
index pack references plus review metadata for a future governed submission
flow. They are review candidates, not truth.

Index packs do not replace source or evidence provenance. Master Index Review
Queue Contract v0 defines how future queue review can compare index summaries
to source, evidence, and contribution packs before any public acceptance.
Validation is not acceptance, and accepted_public is limited,
provenance-bound, and review-governed.

## Runtime Consumers

Future public search, native clients, relay clients, snapshots, hosted search
rehearsals, and review tools may use reviewed index packs to compare coverage,
plan local imports, prepare offline snapshots, or audit source-family breadth.
Before that happens, import and merge planning must define redaction,
deduplication, source trust, conflict handling, reproducibility, and review
gates.

Source/Evidence/Index Pack Import Planning v0 defines validate-only as the
first future mode and stage-local-quarantine as the next future mode. Index
packs remain coverage/build/record-summary metadata, not raw cache exports and
not canonical proof. Planning does not implement import, merge, local index
mutation, public-search mutation, hosted/master-index mutation, or acceptance.

## Not Implemented

Index Pack Contract v0 does not implement index pack import, merge, local cache
export, raw SQLite export, hosted ingestion, upload or contribution intake,
master-index acceptance, live source probes or live connectors, arbitrary URL
fetching, private cache sharing, executable plugin loading, downloads or
installers, accounts, telemetry, auth, TLS, rate limiting, malware safety,
rights clearance, or production extension support.
