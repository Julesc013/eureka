# Candidate Promotion Policy v0

Candidate Promotion Policy v0 defines recommendation-only promotion assessments for provisional candidate records. Promotion policy is not promotion runtime, and candidate promotion runtime is not implemented.

A promotion assessment is not master-index mutation. It cannot accept a candidate as truth, update the candidate index, update source cache or evidence ledger state, update public search ranking, or write the master index.

## Gates

Promotion toward any future authoritative path requires structure, candidate type, source policy, provenance, evidence, privacy, rights, risk, conflict, duplicate, human, policy, and operator gates. AI output, probe output, pack output, and manual observation are not automatic truth.

## Evidence And Provenance

Evidence sufficiency is for future review eligibility only. Candidate-only evidence and AI-only output are insufficient for master-index promotion. Provenance must reference source, pack, validator, or review context before a future review queue can consider it.

## Privacy Rights And Risk

Raw query retention defaults to none. Promotion assessments must not contain private paths, secrets, account identifiers, IP addresses, unsafe private URLs, or unreviewed local result identifiers. Rights clearance and malware safety are not claimed by this policy.

## Decisions

Recommended decisions are recommendation-only: no_action, reject_candidate, quarantine_candidate, request_more_evidence, request_source_policy_review, request_rights_risk_review, mark_duplicate_candidate, supersede_candidate_future, eligible_for_review_queue_future, eligible_for_promotion_future, and not_eligible. Automatic promotion is forbidden.

## Boundaries

Candidate confidence is not truth. Destructive merge is forbidden. Future outputs such as review queue entries, evidence pack candidates, source cache candidates, evidence ledger candidates, rejection records, quarantine records, and master index candidates are not emitted in P65.

## Relations

This policy consumes Candidate Index v0 references and stays downstream of query observations, shared result cache entries, miss ledger entries, search needs, and probe queue items. It is upstream of future known absence pages, privacy/poisoning guard, demand dashboard, source sync worker, source cache/evidence ledger, and master index review queue work.

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

Evidence ledger observations are not accepted truth by default. Candidate promotion policy remains required before any evidence observation can approach authoritative review, and P70 performs no promotion or master-index mutation.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/CANDIDATE_PROMOTION_POLICY.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
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
