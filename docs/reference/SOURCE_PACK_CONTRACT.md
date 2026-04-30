# Source Pack Contract

Source Pack Contract v0 defines a portable, validated bundle of source
metadata and public-safe evidence inputs. It is the first safe extension path
for future users, maintainers, archivists, and connectors to contribute source
knowledge without giving Eureka arbitrary network access, private local
filesystem access, executable plugin authority, or master-index acceptance.

This contract is validation and governance only. It does not implement source
pack import, local indexing, uploads, hosted submission, live connectors,
downloads, installers, executable plugins, or public master-index acceptance.

## Pack Layout

Required files:

- `SOURCE_PACK.json`
- `README.md`
- `RIGHTS_AND_ACCESS.md`
- `CHECKSUMS.SHA256`

Optional files:

- `source_records.jsonl`
- `evidence_records.jsonl`
- `representation_records.jsonl`
- `compatibility_records.jsonl`
- `member_records.jsonl`
- `fixtures/`
- `payloads/`
- `tests/`
- `licenses/`
- `references/`
- `manifests/`

The manifest schema is `contracts/packs/source_pack.v0.json`.

## Manifest

`SOURCE_PACK.json` declares:

- `schema_version`
- `pack_id`
- `pack_version`
- `title`
- `description`
- `status`
- `producer`
- `source_families`
- `source_records`
- `evidence_files`
- `fixture_files`
- `rights_and_access`
- `privacy`
- `capabilities`
- `prohibited_behaviors`
- `checksums`
- `validation`
- `notes`

Status values include `draft`, `local_private`, `shareable_candidate`,
`submitted`, `accepted_public`, `rejected`, and `superseded`. A status is not
acceptance by itself. `accepted_public` requires a future governed review path;
P34 does not create that path.

## Source Records

Source pack source records align with Source Registry v0 vocabulary:

- `source_id`
- `source_family`
- `label`
- `posture`
- `coverage_depth`
- `connector_mode`
- `capabilities`
- `limitations`
- `next_coverage_step`
- `rights_and_access`
- fixture/recorded/local-private flags
- disabled live/network posture

A source pack source record is not automatically canonical. It does not become
a record under `control/inventory/sources/` unless a future review/import
milestone accepts it.

## Evidence Records

Evidence records are JSONL and must stay public-safe. Allowed v0 concepts
include:

- `source_observation`
- `metadata_claim`
- `compatibility_claim`
- `member_path_claim`
- `checksum_observation`
- `version_observation`
- `release_note_observation`
- `manual_document_observation`
- `review_description_observation`
- `absence_observation`

Each record should include an evidence id, source id, subject reference,
evidence kind, claim type, summary or claim value, locator, creator pack, and
limitations. Snippets are optional and must be public-safe.

Forbidden evidence contents include private absolute paths, credentials, API
keys, raw private files, raw copyrighted long-form dumps, malware-safety
assertions, rights-clearance assertions, and executable payloads.

## Difference From Evidence And Index Packs

A source pack can define source metadata, source-family posture, fixture files,
and evidence inputs together. An evidence pack is claim and observation focused:
it carries public-safe evidence records, source references, snippets, and
provenance without defining canonical source registry records or shipping source
fixtures. Both pack types are validation-only until future import and submission
workflows exist.

An index pack is coverage and record-summary focused: it describes index build
metadata, source coverage, field coverage, query examples, and public-safe
record summaries without exporting a raw cache or SQLite database. Source,
evidence, and index packs all remain validation-only until future import,
merge, submission, and review workflows exist.

## Fixture Policy

Allowed fixture payloads:

- synthetic JSON metadata
- small paraphrased or self-authored README text
- small manifest text
- small compatibility note text
- tiny public-domain or self-authored text with rights notes
- checksums for fixture files

Not allowed by v0 default:

- real executables
- real installers
- real copyrighted article, manual, or book scans
- large binaries
- credentialed source exports
- private local file trees
- arbitrary cache dumps

Future binary artifact handling requires a separate artifact/evidence/download
policy milestone.

## Privacy

Packs classify privacy as `public_safe`, `local_private`, `review_required`,
`restricted`, or `unknown`.

The safe default for newly created packs is local-private until validation and
explicit export or submission. Shareable packs must not contain credentials,
private local absolute paths, raw private files, private cache dumps, or local
user identifiers.

## Rights And Access

Every source pack must include `RIGHTS_AND_ACCESS.md`. Source metadata is not
rights clearance, and fixture metadata is not distribution permission. A pack
must not claim malware safety or rights clearance.

## Checksums

`CHECKSUMS.SHA256` records SHA-256 checksums for pack files. Shareable and
submitted packs must include checksums. Production signing is future/deferred
and is not implemented by this contract.

## Validation

Validate the example source pack:

```bash
python scripts/validate_source_pack.py
python scripts/validate_source_pack.py --json
python scripts/validate_source_pack.py --strict
```

Validate another pack:

```bash
python scripts/validate_source_pack.py --pack-root path/to/pack
```

The validator parses the manifest and JSONL files, checks checksums, rejects
public/shareable private-path leaks, rejects executable payload extensions in
v0 examples, requires disabled live/network behavior, and confirms rights
notes exist. It does not import, index, upload, execute, or contact a network.

## Relationship To Other Packs

Source packs answer "what source metadata and fixture evidence inputs exist?"

Evidence packs answer "what normalized evidence envelope can be reviewed and
reused across sources?"

Index packs answer "what index build, source coverage, field coverage, query
examples, and public-safe record summaries exist without sharing a raw cache or
SQLite database?"

Contribution packs answer "what review-submission wrapper carries proposed
changes, referenced packs, reviewer notes, provenance, and acceptance status
through a future review process?"

Master Index Review Queue Contract v0 answers "what queue entry, review
decision, validation, acceptance, conflict, and publication gates are required
before a reviewed pack can become a future public master-index candidate?"
Pack validation is not acceptance, and accepted_public remains limited,
review-governed, and evidence/provenance-bound.

## Consumer Relationships

Future local public search may import validated source packs only after a
separate import/runtime milestone. Public search remains `local_index_only`.

Source/Evidence/Index Pack Import Planning v0 now defines the future
validate-only first path. Source packs must be validated, classified, and, in a
later milestone, staged privately in quarantine before they can become local
index candidates. Planning does not implement import, does not mutate the
canonical source registry, does not change public search, and does not create
master-index acceptance.

Snapshots, native clients, and relay clients may eventually consume
public-safe source-pack summaries through their own contracts. Source Pack v0
does not implement those consumers.

AI provider packs are future and separate. A source pack is not an AI prompt,
agent, executable plugin, or model provider configuration.

## Out Of Scope

P34 does not implement:

- runtime import
- local indexing
- upload handling
- hosted submission
- master-index acceptance
- live source connectors
- live probes
- arbitrary URL fetching
- crawling or scraping
- executable payloads
- downloads or installers
- native clients
- relay runtime
- snapshot reader runtime
- production signing
- accounts, telemetry, auth, TLS, rate limiting, or process management
