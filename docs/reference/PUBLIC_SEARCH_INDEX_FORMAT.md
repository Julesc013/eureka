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

## P72 Wayback/CDX/Memento Connector Approval Pack v0

P72 defines a future availability/capture-metadata-only Wayback/CDX/Memento connector approval pack. The connector is not implemented, no external calls are made, public queries do not fan out to Wayback/CDX/Memento, arbitrary URL fetch is forbidden, archived content fetch/capture replay/WARC download are forbidden, and future outputs must be cache-first/evidence-first after URI privacy review and approval.

<!-- P73-GITHUB-RELEASES-CONNECTOR-APPROVAL-START -->
## P73 GitHub Releases Connector Approval Pack v0

P73 defines a future release-metadata-only GitHub Releases connector approval pack. The live connector is not implemented, no external calls are made, no GitHub API calls are made, public queries do not fan out to GitHub, arbitrary repository fetch is forbidden, repository clone is forbidden, release asset download is forbidden, source archive download is forbidden, raw file/blob/tree fetch is forbidden, scraping/crawling is forbidden, token use is not allowed now, and future outputs must be cache-first/evidence-first after repository identity review and approval.
<!-- P73-GITHUB-RELEASES-CONNECTOR-APPROVAL-END -->

<!-- P74-PYPI-METADATA-CONNECTOR-APPROVAL-START -->
## P74 PyPI Metadata Connector Approval Pack v0

P74 adds an approval-only, package metadata-only PyPI connector pack. It adds no live PyPI connector runtime, no external calls, no PyPI API calls, no package metadata fetch, no release fetch, no wheel/sdist/package file download, no package install, no dependency resolution, no package archive inspection, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Package identity review, dependency metadata caution, source policy review, User-Agent/contact, token policy, rate limits, timeouts, retry/backoff, circuit breaker, cache-first output, and evidence attribution remain approval gates.
<!-- P74-PYPI-METADATA-CONNECTOR-APPROVAL-END -->

<!-- P75-NPM-METADATA-SUMMARY-START -->
## P75 npm Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live npm connector runtime, no external calls, no npm registry API calls, no npm/yarn/pnpm CLI calls, no package metadata fetch, no version fetch, no dist-tag fetch, no tarball metadata fetch, no tarball download, no package file download, no package install, no dependency resolution, no package archive inspection, no lifecycle script execution, no npm audit, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires package identity review, scoped package review, dependency metadata caution, lifecycle script risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P76 Software Heritage Connector Approval Pack v0.
<!-- P75-NPM-METADATA-SUMMARY-END -->

<!-- P76-SOFTWARE-HERITAGE-SUMMARY-START -->
## P76 Software Heritage Connector Approval Pack v0

Completed as an approval-only software identity/archive metadata connector pack. It adds no live Software Heritage connector runtime, no external calls, no Software Heritage API calls, no SWHID resolution, no origin/visit/snapshot/release/revision/directory/content lookup, no source code download, no repository clone, no source archive download, no source file retrieval, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires SWHID/origin/repository identity review, source-code-content risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P77 Public Hosted Deployment Evidence v0.
<!-- P76-SOFTWARE-HERITAGE-SUMMARY-END -->

## P77 Public Index Evidence

Repo-local public index artifacts exist, but the configured static URL returned 404 for `/data/public_index_summary.json`, so deployed public-index availability is not verified.

<!-- P78-EXTERNAL-BASELINE-COMPARISON-START -->
## P78 External Baseline Comparison Report v0

P78 added local-only comparison readiness for manual external baselines. Current eligibility is `no_observations`: Batch 0 has 0 observed records and 39 pending slots. No web calls, source API calls, model calls, fabricated observations, fabricated comparisons, production readiness claim, or index/cache/ledger/candidate/master-index mutation were made. Codex-safe next branch is P79 Object Page Contract v0 while Manual Observation Batch 0 remains human-operated.
<!-- P78-EXTERNAL-BASELINE-COMPARISON-END -->

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0

Object Page Contract v0 is contract-only and evidence-first. It defines future public object pages that preserve provisional identity, source/evidence/provenance, compatibility, conflicts, scoped absence, and gaps without implementing runtime object pages.

Boundary notes:

- No runtime object routes, database, persistent object-page store, source connector runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, or malware safety claim are added.
- Public search may reference object page links only after a future governed integration; P79 does not mutate public search result cards or the public index.
- Object pages are not app-store, downloader, installer, or execution surfaces.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Source Page Contract v0 is contract-only and evidence-first. It defines future public source pages for source identity, status, coverage, connector posture, source policy gates, source cache/evidence posture, public search projection, query-intelligence projection, limitations, provenance caution, and rights/risk posture.

Boundary notes:

- No runtime source routes, database, persistent source-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, mirrors, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, or authoritative source trust claim are added.
- Public search may reference source page links or source badges only after a future governed integration; P80 does not mutate public search result cards or the public index.
- Source pages explain source posture and limitations; they are not source API proxies, scrapers, crawlers, download pages, mirrors, or connector health dashboards.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->

<!-- P81-COMPARISON-PAGE-CONTRACT-START -->
## P81 Comparison Page Contract v0

Comparison Page Contract v0 is contract-only and evidence-first. It defines future public comparison pages for subjects, criteria, matrices, identity/version/representation/source/evidence/compatibility/action comparisons, conflict preservation, scoped gaps, and future result-card/object/source projections.

Boundary notes:

- No runtime comparison pages, database, persistent comparison-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, authoritative source trust claim, or winner without evidence are added.
- Public search may reference comparison links only after a future governed integration; P81 does not mutate public search result cards or the public index.
- Comparison pages explain evidence-backed similarity, difference, conflict, and gaps; they are not ranking authority, candidate promotion, source API proxies, download pages, installer pages, or production comparison services.
<!-- P81-COMPARISON-PAGE-CONTRACT-END -->

<!-- P82-CROSS-SOURCE-IDENTITY-RESOLUTION-START -->
## P82 Cross-Source Identity Resolution Contract v0

Cross-Source Identity Resolution Contract v0 is contract-only and evidence-first. It defines future identity relation assessments and provisional clusters for exact, likely, possible, variant, version, release, representation, member, package, repository, capture, alias, near-match, different, conflicting, and unknown relations.

Boundary notes:

- No runtime identity resolver, persistent identity store, cluster runtime, merge runtime, destructive deduplication, records merged, candidate promotion, master-index mutation, public-index mutation, source-cache mutation, evidence-ledger mutation, candidate-index mutation, live source fanout, downloads, installs, execution, telemetry, accounts, source trust, rights clearance, malware safety claim, or identity truth overclaim are added.
- Public search, object pages, source pages, and comparison pages may reference identity relation labels only after future governed integration; P82 does not mutate public search or public index.
- Identity confidence is not identity truth; names and aliases alone are weak evidence; conflicts are preserved.
<!-- P82-CROSS-SOURCE-IDENTITY-RESOLUTION-END -->

<!-- P83-RESULT-MERGE-DEDUPLICATION-START -->
## P83 Result Merge and Deduplication Contract v0

P83 defines contract-only search-result grouping and deduplication semantics. It preserves alternatives, conflicts, source/evidence/provenance refs, and user-visible explanations while forbidding runtime grouping, result suppression, ranking changes, destructive merge, candidate promotion, live source calls, telemetry, and index/cache/ledger mutation.

Future public search, object/source/comparison pages, cross-source identity resolution, and ranking contracts may reference P83 only after governed runtime planning.
<!-- P83-RESULT-MERGE-DEDUPLICATION-END -->

<!-- P84-EVIDENCE-WEIGHTED-RANKING-START -->
## P84 Evidence-Weighted Ranking Contract v0

P84 defines contract-only evidence-weighted ranking assessments and public explanations. It is explanation-first ranking by evidence quality, provenance, source posture, freshness, conflict state, candidate/provisional status, action safety, rights/risk caution, and gap transparency.

P84 adds no runtime ranking, production ranking, public search order change, hidden suppression, result hiding, candidate promotion, source trust authority, popularity/telemetry/ad/user-profile ranking, model calls, live source fanout, downloads, installs, execution, or source-cache/evidence-ledger/candidate/public/local/runtime/master-index mutation.

Future public search, result merge groups, object/source/comparison pages, and ranking-runtime planning may reference P84 only after governed runtime planning and eval evidence.
<!-- P84-EVIDENCE-WEIGHTED-RANKING-END -->

<!-- P85-COMPATIBILITY-AWARE-RANKING-START -->
## P85 Compatibility-Aware Ranking Contract v0

P85 adds a contract-only compatibility-aware ranking layer. It defines public-safe target profiles, compatibility factors, cautious explanations, no installability without evidence, no emulator/VM or package-manager launch, no runtime ranking, no public search order change, no hidden suppression, and no index/cache/ledger/candidate/master-index mutation.
<!-- P85-COMPATIBILITY-AWARE-RANKING-END -->
<!-- P95-DEEP-EXTRACTION-CONTRACT-START -->
## P95 Deep Extraction Contract v0

P95 adds Deep Extraction Contract v0 as contract/schema/example/validator work only. It defines metadata-first extraction requests, result summaries, policies, tiers, container/member/manifest/text/OCR hooks, sandbox/resource requirements, privacy/path/secret rejection, executable-risk labels, provenance, synthetic-record boundaries, and future relationships to source cache, evidence ledger, candidate records, public search, object pages, comparison pages, and result explanations.

No extraction runtime is implemented. No files are opened, archives unpacked, payloads executed, package managers invoked, emulators or VMs launched, OCR/transcription performed, URLs fetched, live sources called, source/evidence/candidate/index records mutated, or candidates promoted.
<!-- P95-DEEP-EXTRACTION-CONTRACT-END -->
