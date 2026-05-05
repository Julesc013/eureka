# Candidate Index Contract v0

Status: contract-only in P64.

Candidate index records are provisional, reviewable records for possible
objects, identities, source matches, evidence, compatibility statements,
members, extraction outputs, absence summaries, or query interpretations.
A candidate is not truth. It is not accepted evidence, not public search
authority, not a source-cache record, not an evidence-ledger record, not a
probe job, and not a master-index record.

P64 defines schema, examples, validation, docs, and audit evidence only. There
is no runtime candidate index, no persistent candidate store, no public search
candidate injection, no candidate promotion runtime, no source-cache mutation,
no evidence-ledger mutation, no local-index mutation, and no master-index
mutation.

## Record Shape

`contracts/query/candidate_index_record.v0.json` requires:

- `candidate_identity`: non-reversible `sha256` fingerprint, canonical public
  label, normalized terms, aliases, and optional future duplicate links.
- `candidate_type`: candidate type taxonomy, type family, and future-only
  destination labels.
- `candidate_subject`: public-safe object/source/evidence/absence subject
  hints.
- `candidate_claims`: unreviewed or review-required claims with confidence and
  limitations.
- `provenance` and `input_refs`: references to query observations, shared
  result cache entries, miss ledger entries, search needs, probe items, packs,
  manual observations, or future typed outputs.
- `evidence_refs`: candidate or missing evidence references; these are not
  accepted evidence.
- `source_policy`: no-source-call or future approved source reference posture.
- `confidence`: confidence class, basis, notes, and the hard
  confidence-not-truth flag.
- `review`: review status, required reviews, promotion gate, and promotion
  policy requirement.
- `conflicts`: duplicate and conflict preservation model.
- `visibility`: public result visibility is false in v0 examples.
- `privacy`, `rights_and_risk`, `retention_policy`, `limitations`,
  `no_truth_guarantees`, and `no_mutation_guarantees`.

## Candidate Type Taxonomy

P64 defines these candidate types:

- `object_identity_candidate`
- `software_version_candidate`
- `source_record_candidate`
- `evidence_record_candidate`
- `representation_candidate`
- `member_path_candidate`
- `compatibility_claim_candidate`
- `checksum_candidate`
- `release_metadata_candidate`
- `package_metadata_candidate`
- `source_match_candidate`
- `identity_match_candidate`
- `alias_candidate`
- `absence_candidate`
- `extraction_candidate`
- `OCR_text_candidate`
- `query_interpretation_candidate`
- `actionability_candidate`
- `unknown`

Type families are `object`, `source`, `evidence`, `representation`, `member`,
`compatibility`, `identity`, `absence`, `extraction`, `query`,
`actionability`, and `unknown`.

Allowed future destinations are labels only:
`evidence_pack_candidate`, `contribution_pack_candidate`,
`candidate_index_only`, `master_index_review_queue_future`,
`source_cache_future`, and `evidence_ledger_future`.

## Lifecycle

Candidate lifecycle states include `draft_example`, `dry_run_validated`,
`observed_future`, `normalized_future`, `candidate_future`,
`review_required`, `quarantined`, `rejected_future`, `superseded_future`, and
`promoted_future`.

`promoted_future` is a future vocabulary value, not current acceptance. P64
examples keep `accepted_as_truth`, `promoted_to_master_index`, and
`promotion_allowed_now` false. Candidate promotion is not implemented.

## Confidence And Review

Candidate confidence is an input to review, not acceptance. The
confidence-not-truth flag must be true even when confidence is medium or high.

Review states include structural validity, evidence review, human review,
policy review, rights review, risk review, conflict review, future rejection,
and future promotion. `promotion_policy_required` is true and
`promotion_allowed_now` is false in v0.

## Provenance And Inputs

Candidate records may reference earlier query-intelligence contracts:

- query observations
- shared query/result cache entries
- search miss ledger entries
- search need records
- probe queue items

They may also reference future manual observations, source packs, evidence
packs, contribution packs, typed AI outputs, source-cache records, or probe
results. These are references only. P64 imports no packs, runs no probes, calls
no external sources, and accepts no public contribution automatically.

## Conflicts

Candidates preserve uncertainty. Conflict states include possible duplicate,
identity conflict, version conflict, source conflict, compatibility conflict,
evidence conflict, rights/access conflict, and unknown.

The preservation policy is `preserve_conflict`, `review_required`, or
`not_applicable`. P64 does not destructively merge or choose truth from
conflicting candidates.

## Source, Evidence, Rights, And Risk

Source policy kinds include `no_source_call`, `fixture_only`,
`recorded_fixture`, `source_cache_future`, `evidence_pack_reference`,
`source_pack_reference`, `live_probe_after_approval_future`, and `unknown`.

Public-safe examples keep live source calls and live probes disabled. Rights
clearance and malware safety are not claimed. Downloads, installs, and
execution are false.

## Privacy

Raw query retention default is `none`. Candidate records must not include raw
private queries, IP addresses, account IDs, private paths, sensitive tokens,
private URLs, local result IDs, executable payloads, or raw copyrighted payload
dumps.

Public aggregate use is future-only after privacy filtering. Individual
candidate records are not publishable by default.

## Public Visibility

Candidate records are not current public search authority. V0 examples keep
`public_result_visibility_allowed` false. A future product could decide to show
reviewed provisional labels, but that requires a separate policy and UI
contract.

## Runtime Boundary

The optional dry-run helper emits JSON to stdout only. Public search routes do
not write candidate records and do not use candidate records for ranking.
Future runtime integration requires a separate candidate promotion policy,
privacy and poisoning guard, source/evidence ledger contracts, review queue
contract, and no-mutation verification.

## P65 Candidate Promotion Policy Relationship

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

P65 does not implement candidate promotion runtime. Candidate confidence remains not truth, even when a future promotion assessment recommends review queue eligibility.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Query Privacy and Poisoning Guard v0 is future/contract-only. It should classify privacy risks, poisoning risks, redaction, public aggregate eligibility, and future query-intelligence eligibility before this record type is used for learning. P67 does not mutate this record type, add telemetry, track accounts or IPs, persist guard decisions, or alter public search runtime behavior.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.

## Source Sync Worker v0 Relation

Source Sync Worker Contract v0 is future/contract-only. It may later consume probe queue and demand dashboard signals to plan approved, bounded source sync jobs, but P69 adds no connector runtime, source calls, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or index mutation.

## P70 Source Cache And Evidence Ledger Relation

Source cache records and evidence ledger observations may later become inputs for candidate records only after validation and review. P70 does not create candidates, promote candidates, or mutate candidate/public/local/master indexes.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/CANDIDATE_INDEX_CONTRACT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
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
