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
Validate-Only Pack Import Tool v0 may run this contract validator for an
explicit evidence pack root and emit Pack Import Report v0, but that report is
still not import, staging, indexing, upload, canonical truth selection, or
master index acceptance.
Local Quarantine/Staging Model v0 may later stage evidence metadata as a
local_private candidate linked to a validate-only report, but it creates no
staging runtime and does not turn evidence records into truth, search input, or
master-index state.

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
candidates, not truth. Master Index Review Queue Contract v0 defines the
future queue entry and decision model for deciding which public-safe claims and
summaries may become limited accepted-public candidates. P35, P36, P37, and P38
implement none of those runtime or hosted workflows.

## Runtime Consumers

Future public search, native clients, relay clients, snapshots, and review tools
may read reviewed evidence packs to populate result-card evidence,
compatibility caveats, source locator summaries, absence reports, and
provenance. Before that happens, import planning must define redaction,
deduplication, source trust, conflict handling, and review gates.

Source/Evidence/Index Pack Import Planning v0 defines that first boundary as
validate-only before private local quarantine. Evidence packs remain
claims/observations, not truth. Planning does not implement import, indexing,
public-search mutation, canonical registry mutation, master-index mutation, or
automatic acceptance.

Pack Import Validator Aggregator v0 now validates the evidence-pack example
through `python scripts/validate_pack_set.py --all-examples` or an explicit
`--pack-root`. Aggregated validation delegates to `validate_evidence_pack.py`
and does not import, stage, index, upload, or make evidence canonical.

Pack Import Report Format v0 now defines the future report envelope for
recording evidence-pack validation outcomes. Reports can preserve failed,
review-required, or passed evidence-pack checks, but a report is not evidence
acceptance and does not import, stage, index, upload, mutate public search, or
mutate the master index.

AI Provider Contract v0 is separate from evidence packs. AI output is not
evidence truth. Typed AI Output Validator v0 now provides
`scripts/validate_ai_output.py` for offline typed output validation before any
future AI-assisted evidence drafting. Future AI output may draft evidence
candidates only when typed, validated, linked to source/evidence references
where possible, and reviewed. It does not enter evidence packs automatically
and cannot bypass evidence-pack validation, rights/privacy checks, contribution
review, or master-index review.

AI-Assisted Evidence Drafting Plan v0 defines that future candidate mapping in
`docs/reference/AI_ASSISTED_DRAFTING_CONTRACT.md`. A metadata,
compatibility, review-description, member-path, source-observation,
OCR-cleanup, or absence candidate must pass typed output validation first and
remain review-required. The plan adds no AI runtime, no model calls, no
evidence import, no public search mutation, no local index mutation, and no
master-index mutation.

## Not Implemented

Evidence Pack Contract v0 does not implement evidence pack import, local or
hosted indexing, upload or contribution intake, master-index acceptance, live
source probes or live connectors, arbitrary URL fetching, private cache sharing,
executable plugin loading, downloads or installers, accounts, telemetry, auth,
TLS, rate limiting, malware safety, rights clearance, or production extension
support.
## P64 Candidate Index Note

Candidate evidence refs are not evidence-pack acceptance. A future candidate
may point toward an evidence-pack candidate, but P64 imports no packs, writes no
evidence ledger, claims no rights clearance, and accepts no candidate evidence
as authoritative.

## P65 Candidate Promotion Boundary

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.
