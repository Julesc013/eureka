# Evidence Pack Contract

Evidence Pack Contract v0 defines a portable, validated bundle of public-safe
claims and observations. It lets future users, maintainers, archivists, and
review workflows share source locators, compatibility notes, member-path notes,
absence notes, snippets, and provenance without sharing a full source pack, a
local index, a private cache, executable payloads, or private local paths.

This contract is validation and governance only. It does not implement evidence
pack import, indexing, uploads, hosted submission, live connectors, downloads,
installers, executable plugins, master-index acceptance, or canonical truth
selection.

## Pack Layout

Required files:

- `EVIDENCE_PACK.json`
- `README.md`
- `RIGHTS_AND_ACCESS.md`
- `CHECKSUMS.SHA256`
- `evidence_records.jsonl`

Optional files:

- `source_references.jsonl`
- `compatibility_claims.jsonl`
- `member_claims.jsonl`
- `absence_claims.jsonl`
- `identity_claims.jsonl`
- `review_notes.jsonl`
- `snippets/`
- `manifests/`
- `tests/`
- `licenses/`
- `references/`

The manifest schema is `contracts/packs/evidence_pack.v0.json`.

## Manifest

`EVIDENCE_PACK.json` declares `schema_version`, `pack_id`, `pack_version`,
`title`, `description`, `status`, `producer`, `privacy`, `rights_and_access`,
`evidence_files`, `source_reference_files`, `checksum_policy`, `validation`,
`prohibited_contents`, and `notes`.

Lifecycle statuses follow Pack Lifecycle guidance: `draft`, `local_private`,
`validated_local`, `shareable_candidate`, `submitted`, `quarantined`,
`review_required`, `accepted_public`, `rejected`, and `superseded`. A lifecycle
status does not grant import, upload, indexing, network, plugin, or
master-index authority. `accepted_public` requires a future governed review
path; P35 does not create that path.

## Evidence Records

Evidence records are JSONL objects. Each record should include `evidence_id`,
`evidence_kind`, `claim_type`, `subject_ref`, `source_ref` or `source_id`,
`locator`, `summary`, optional `claim_value`, optional short `snippet`,
optional `confidence`, optional `observed_at`, optional `asserted_by`,
`created_by_pack`, `limitations`, `privacy_classification`, and
`rights_classification`.

Evidence records are claims and observations, not canonical truth. A
compatibility claim reports evidence; it is not a universal compatibility
oracle. An absence observation is scoped to the pack or checked source; it is
not proof that something does not exist globally.

## Evidence Kinds And Claim Types

Allowed v0 evidence kinds are `source_observation`, `metadata_claim`,
`compatibility_claim`, `member_path_claim`, `checksum_observation`,
`version_observation`, `release_note_observation`,
`manual_document_observation`, `review_description_observation`,
`absence_observation`, `identity_candidate`, `provenance_note`, and
`actionability_note`.

Allowed v0 claim types are `describes`, `mentions`, `supports_platform`,
`does_not_support_platform`, `requires_runtime`, `has_version`,
`latest_known_for_platform`, `contains_member`, `has_checksum`,
`documents_hardware`, `documents_install_step`, `reports_works_on`,
`reports_failure_on`, `source_missing`, `dead_link_observed`,
`archived_trace_exists`, `same_as_candidate`, `variant_of_candidate`,
`evidence_for_absence`, and `actionability_hint`.

These types are intentionally narrow enough to feed future public search result
cards while keeping truth selection and review separate.

## Source References

`source_references.jsonl` can identify where a claim came from without granting
live-fetch behavior. A source reference may include `source_ref`, optional
`source_id`, optional `source_family`, `label`, `locator`, `locator_kind`,
`network_required_to_verify`, `rights_notes`, and `limitations`.

Allowed locator kinds are `fixture_locator`, `source_url_reference`,
`archive_identifier_reference`, `package_identifier`, `manual_reference`, and
`local_private_reference`.

A source URL reference is a locator only. It is not permission to fetch a URL,
scrape a site, call an API, or add a live source connector.

## Snippet Policy

Snippets must be short, public-safe, cited or located, and under the v0
validator threshold of 500 characters. Snippets must not contain credentials,
private paths, private files, raw copyrighted long-form text, malware-safety
assertions, or rights-clearance assertions.

Evidence packs may omit snippets and use summaries instead when rights or
privacy are unclear.

## Privacy

Pack and record privacy classes are `public_safe`, `local_private`,
`review_required`, `restricted`, and `unknown`.

The safe default while authoring is local-private. `shareable_candidate` and
`submitted` packs must not contain local-private records, credentials, private
absolute paths, private cache exports, or restricted snippets. `accepted_public`
requires future review and must not contain review-required, restricted, or
local-private records.

## Rights And Access

Every evidence pack must include `RIGHTS_AND_ACCESS.md`.

Evidence is not rights clearance. Metadata and claims are not artifact
distribution permission. Snippets may still be subject to source rights.
Evidence packs do not include executables, installers, raw private files, or raw
copyrighted long-form text by default. Future public or master-index acceptance
requires a separate review workflow.

## Checksums

`CHECKSUMS.SHA256` records SHA-256 checksums for pack files, excluding the
checksum file itself. Shareable and submitted packs must include checksums.
Production signing is future/deferred and is not implemented by this contract.

## Validation

Validate the example evidence pack:

```bash
python scripts/validate_evidence_pack.py
python scripts/validate_evidence_pack.py --json
python scripts/validate_evidence_pack.py --strict
```

The validator checks manifest fields, JSONL parsing, evidence id uniqueness,
allowed evidence kinds and claim types, source references, privacy/status
consistency, snippet length, checksums, rights docs, private paths, prohibited
credential fields, executable payload extensions, and no live network behavior.

The validator does not import, index, upload, execute, fetch, scrape, or accept
evidence into a master index.

## Relationship To Other Packs

Source packs define source metadata plus optional fixture/evidence inputs.
Evidence packs are narrower: they carry claims and observations and do not
register sources by themselves.

Index packs describe index build metadata, source coverage, field coverage,
query examples, and public-safe record summaries without exporting raw caches
or SQLite databases. Contribution packs wrap proposed changes, referenced
packs, manual-observation placeholders, and review metadata as review
candidates, not truth. The master index review queue is future and would decide
which public-safe claims and summaries can become accepted records. P35, P36,
and P37 implement none of those runtime or hosted workflows.

## Runtime Consumers

Future public search, native clients, relay clients, snapshots, and review tools
may read reviewed evidence packs to populate result-card evidence,
compatibility caveats, source locator summaries, absence reports, and
provenance. Before that happens, import planning must define redaction,
deduplication, source trust, conflict handling, and review gates.

## Not Implemented

Evidence Pack Contract v0 does not implement evidence pack import, local or
hosted indexing, upload or contribution intake, master-index acceptance, live
source probes or live connectors, arbitrary URL fetching, private cache sharing,
executable plugin loading, downloads or installers, accounts, telemetry, auth,
TLS, rate limiting, malware safety, rights clearance, or production extension
support.
