# Public Search Index Format v0

Public Search Index v0 is a committed, deterministic, public-safe index bundle
for `local_index_only` public search.

## Query Intelligence Cache Boundary

P60 shared query/result cache examples reference the public index build and
manifest so future cached summaries can be invalidated when the index changes.
P61 search miss ledger examples reference the public index build and checked
scope so scoped absence and weak hits stay tied to a concrete public index
snapshot. The public index builder does not write query cache entries, miss
ledgers, search needs, probes, candidate indexes, or master-index records.

## Artifact Root

`data/public_index/`

Required files:

- `build_manifest.json`
- `source_coverage.json`
- `index_stats.json`
- `search_documents.ndjson`
- `checksums.sha256`

The committed bundle is JSON/NDJSON text only. `eureka.sqlite` is not committed
in v0; SQLite and FTS5 availability are detected and recorded, but the runtime
uses deterministic lexical fallback over the generated documents.

## Document Model

Each line in `search_documents.ndjson` is a JSON object with stable public fields:

- `doc_id`, `record_id`, `record_kind`
- `title`, `subtitle`, `description`
- `source_id`, `source_family`, `source_status`, `source_coverage_depth`
- `object_family`, `representation_kind`, `member_path`, `parent_ref`
- `platform_terms`, `architecture_terms`, `version_terms`, `date_terms`, `keyword_terms`
- `compatibility_summary`, `evidence_summary`
- `result_lane`, `user_cost_summary`
- `allowed_actions`, `blocked_actions`
- `warnings`, `limitations`
- `public_target_ref`
- `search_text`

The index must not include absolute local paths, credentials, executable
payloads, private cache roots, raw user uploads, live API responses, or raw
copyrighted payload dumps.

P57 Public Search Safety Evidence v0 validates this bundle as a public-safe
artifact: document counts match the static summary, live/private/executable
flags are false, dangerous actions are not enabled, and no private path or
secret marker is recorded in the evidence output.

P56 exposes a static summary of this bundle at
`site/dist/data/public_index_summary.json`. That summary is publication data,
not dynamic search execution and not a hosted backend claim.

## Runtime Contract

Public search may load this bundle from the repository-owned
`data/public_index` path. Public requests must not choose an index path,
database path, source root, local path, store root, or filesystem root.

Result cards remain governed by `PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`.
Actions stay safe: inspect, view source, view provenance, and read public-safe
summary text. Downloads, uploads, installs, execution, live probes, and arbitrary
URL fetching remain blocked.
## P58 Hosted Rehearsal Compatibility

P58 verifies that the hosted wrapper can read the generated public index during
localhost rehearsal and that the static public index summary still matches the
committed public-safe index counts.

## P62 Search Need Compatibility

P62 search need records may cite the public index build or snapshot as checked
scope. They do not mutate the public index, import packs, stage packs, enqueue
probes, create candidates, or mutate the master index.

## P63 Probe Queue Compatibility

P63 probe queue items may cite public index build or snapshot refs as checked
scope for a future work request. They do not mutate the public index, import
packs, stage packs, run probes, mutate source caches or evidence ledgers, create
candidates, or mutate the master index.
## P64 Candidate Index Note

The public index format remains generated from controlled public-safe index
artifacts. P64 does not add candidate records to the public index, mutate the
public index, or treat candidate confidence as ranking truth.

## P65 Candidate Promotion Boundary

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Query Privacy and Poisoning Guard v0 is future/contract-only. Public search docs reference it as a future privacy/poisoning decision layer only; no runtime guard, telemetry, account/IP tracking, demand dashboard, public search mutation, index mutation, or production abuse protection is claimed.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.

## Source Sync Worker v0 Relation

Source Sync Worker Contract v0 is future/contract-only. It may later consume probe queue and demand dashboard signals to plan approved, bounded source sync jobs, but P69 adds no connector runtime, source calls, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or index mutation.

## P70 Source Cache And Evidence Ledger Relation

Source cache records and evidence ledger observations are future-reviewed inputs only. The public search index format is not mutated by P70, and public search must not expose cache or ledger records as accepted truth without governed review.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/PUBLIC_SEARCH_INDEX_FORMAT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->
