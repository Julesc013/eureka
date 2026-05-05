# Probe Queue Contract v0

Status: contract-only in P63.

Probe queue items are future work requests derived from privacy-filtered search
needs, miss summaries, result-cache summaries, or query observations. They are
not probe execution, not a runtime worker, not connector execution, not source
cache or evidence ledger mutation, not candidate-index mutation, not
master-index truth, and not telemetry.

P63 defines schema, examples, validation, docs, and audit evidence only. It
adds no runtime probe queue, no persistent queue, no telemetry, no public query
logging, no execution, no source calls, no live probes, no source cache
mutation, no evidence ledger mutation, no candidate-index mutation, no
local-index mutation, and no master-index mutation.

## Record Shape

`contracts/query/probe_queue_item.v0.json` requires:

- `probe_identity`: non-reversible `sha256` fingerprint, public-safe canonical
  probe label, and normalized probe terms.
- `probe_kind`: kind taxonomy, future execution class, future live-network
  requirement, and approval/operator/human gates.
- `source_policy`: source policy kind, allowed/prohibited source families,
  disabled live-probe flag, and source/rights review requirements.
- `input_refs`: references to query observations, shared result cache entries,
  search miss ledger entries, search need records, and future reviewed inputs.
- `target`: public-safe target kind and optional product/source/evidence hints.
- `priority` and `scheduling`: example/future priority and scheduling policy;
  no real schedule is created.
- `expected_outputs`: future-only output kinds and destination policies.
- `safety_requirements`: required download/install/execute/upload/path/token/URL
  prohibitions plus future rate-limit, timeout, backoff, and circuit-breaker
  requirements where a future live-network probe would be needed.
- `privacy`, `retention_policy`, `aggregation_policy`, `limitations`,
  `no_execution_guarantees`, and `no_mutation_guarantees`.

## Probe Kind Taxonomy

P63 defines these probe kinds:

- `manual_observation`
- `source_cache_refresh`
- `source_metadata_probe`
- `source_identifier_probe`
- `wayback_availability_probe`
- `package_metadata_probe`
- `repository_release_probe`
- `deep_container_extraction`
- `member_enumeration`
- `OCR_or_scan_extraction`
- `compatibility_evidence_request`
- `source_pack_request`
- `evidence_pack_request`
- `index_pack_request`
- `query_parser_improvement_request`
- `unknown`

Execution classes are future-only: `human_operated_future`,
`scheduled_worker_future`, `approval_gated_live_probe_future`,
`local_offline_extraction_future`, `connector_runtime_future`, and
`no_execution_v0`.

If `live_network_required_future` is true, `approval_required` must be true.
The P63 examples keep `source_policy.live_probe_enabled` false.

## Source Policy And Approval

Allowed source policy kinds are `no_source_call`, `manual_only`,
`fixture_only`, `source_cache_only_future`,
`live_metadata_probe_after_approval`,
`local_offline_extraction_after_approval`, and `unknown`.

Future live-network probe work requires source policy review, operator setup,
rate limits, timeout, retry backoff, circuit breaker controls, and cache before
public reuse. P63 performs none of that work.

## Expected Output Model

Expected output kinds are future-only planning categories such as
`manual_observation`, `source_cache_record`, `evidence_record_candidate`,
`candidate_index_record`, `absence_evidence`, `source_pack_request`,
`evidence_pack_request`, `extraction_report`, and `query_parser_issue`.

Output destination policies are `no_output_v0`, `source_cache_future`,
`evidence_ledger_future`, `candidate_index_future`, `manual_report_future`, or
`contribution_candidate_future`. These names describe future review paths and do
not mutate any store in P63.

## Candidate Index Relationship

P64 adds a candidate index contract-only layer for provisional review records.
Probe queue items may later point toward candidate review through future-only
expected output labels, but P63 does not create candidate index records, does
not execute probes, and does not mutate source cache, evidence ledger, public
search, or the master index.

## Privacy

Raw query retention default is `none`. Public-safe probe queue items must not
contain raw private queries, IP addresses, account IDs, private paths, sensitive
tokens, private URLs, user identifiers, local result IDs, executable payloads,
or raw copyrighted payload dumps.

Aggregate publication is future-only and must exclude raw queries and private
identifiers.

## Runtime Boundary

The optional dry-run helper emits JSON to stdout only. Public search routes do
not write probe queue items. Future runtime integration requires separate
privacy/poisoning guards, source policy, approval evidence, rate limits,
timeouts, circuit breakers, source cache/evidence ledger contracts, candidate
contracts, and no-mutation review.

## P65 Candidate Promotion Policy Relationship

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

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

Probe queue items may later suggest approved source sync work whose outputs enter Source Cache Contract v0 and Evidence Ledger Contract v0. P70 is contract-only and does not enqueue probes, run probes, write source cache records, write evidence ledger records, or mutate indexes.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/PROBE_QUEUE_CONTRACT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
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
