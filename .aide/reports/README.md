# AIDE Reports

This directory is reserved for repo-operating reports. It does not contain
product runtime state and should not be treated as a source of product truth.

Native Action / Download / Install Policy v0 records policy/contract
validation for future action, download, install handoff, package-manager
handoff, mirror, execute, executable-risk, and rights/access behavior without
implementing downloads, installers, package-manager integration, malware
scanning, rights clearance, native clients, relay runtime, or executable trust
claims.

Audit reports that belong under version control should usually live in
`control/audits/` with structured findings. Temporary local run output should
stay outside the repo unless a prompt explicitly asks for a committed evidence
artifact.

Search Usefulness Backlog Triage v0 records its governed backlog under
`control/backlog/search_usefulness_triage/`. If an operator later captures a
triage review report, keep it as evidence here and leave runtime behavior in
the product layers.

Search Usefulness Audit Delta v0 records its committed audit/reporting pack
under `control/audits/search-usefulness-delta-v0/`. It is the canonical place
for the current usefulness-delta summary; do not duplicate volatile local audit
run dumps here.

Search Usefulness Audit Delta v1 records the post-source-expansion delta under
`control/audits/search-usefulness-delta-v1/`. It is also reporting-only and
does not belong in runtime state.

Hard Eval Satisfaction Pack v0 records the archive-resolution hard-eval
satisfaction pass under `control/audits/hard-eval-satisfaction-v0/`. It is
source-backed eval evidence, not AIDE runtime state.

Old-Platform Result Refinement Pack v0 records the archive-resolution
result-shape refinement pass under
`control/audits/old-platform-result-refinement-v0/`. It is deterministic eval
evidence, not AIDE runtime state.

Generated Public Data Summaries v0 records committed static machine-readable
summaries under `site/dist/data/`. No separate AIDE runtime report is needed;
those JSON files are publication artifacts, not AIDE product state.

Lite/Text/Files Seed Surfaces v0 records committed static compatibility
surfaces under `site/dist/lite/`, `site/dist/text/`, and
`site/dist/files/`, with generated validation copies under `site/dist/`.
No separate AIDE runtime report is needed; those files are publication
artifacts and do not add live search, downloads, snapshots, relay behavior, or
native-client runtime.

Public Search Static Handoff v0 records its static handoff artifacts under
`site/dist/search.html`, `site/dist/lite/search.html`,
`site/dist/text/search.txt`, `site/dist/files/search.README.txt`, and
`site/dist/data/search_handoff.json`, plus inventory and validation under
`control/inventory/publication/` and `scripts/`. No separate AIDE runtime
report is needed; this is static publication only and does not add backend
hosting, fake hosted URLs, live probes, downloads, uploads, local path search,
telemetry, or production claims.

Static Resolver Demo Snapshots v0 records committed static resolver examples
under `site/dist/demo/`, with generated validation copies under
`site/dist/demo/`. No separate AIDE runtime report is needed; those files are
publication artifacts and do not add live search, live API semantics, backend
hosting, external observations, or production behavior.

Custom Domain / Alternate Host Readiness v0 records readiness inventories under
`control/inventory/publication/` and operations/reference docs under `docs/`.
No separate AIDE runtime report is needed; this is host-portability governance
only and does not add DNS records, `CNAME`, provider config, alternate-host
deployment, backend hosting, live probes, or production behavior.

Live Backend Handoff Contract v0 records future `/api/v1` handoff inventories
under `control/inventory/publication/` and architecture/reference docs under
`docs/`. No separate AIDE runtime report is needed; this is contract-only
publication governance and does not host a backend, make `/api/v1` live, enable
live probes, implement CORS/auth/rate limits, or create production API
guarantees.

Live Probe Gateway Contract v0 records disabled-by-default source-probe policy
under `control/inventory/publication/` and architecture/reference/operations
docs under `docs/`. No separate AIDE runtime report is needed; this is
contract and policy governance only and does not implement probes, call
external sources, fetch URLs, scrape, crawl, enable downloads, or make Google a
live probe source.

Compatibility Surface Strategy v0 records cross-surface strategy, capability
and route matrices, old-client degradation policy, native-client readiness, and
snapshot/relay readiness notes under `control/inventory/publication/` and
`docs/`. No separate AIDE runtime report is needed; this is strategy and
contract governance only and does not add runtime behavior, snapshots, relay
services, native apps, live backend routes, live probes, or frontend
frameworks.

Signed Snapshot Format v0 records its contract, schema notes, generator,
validator, and deterministic seed example under `control/inventory/publication/`,
`docs/reference/`, `scripts/`, and `snapshots/examples/static_snapshot_v0/`.
No separate AIDE runtime report is needed; this is static export governance and
does not add real signing keys, production signatures, executable downloads, a
public `/snapshots/` route, relay behavior, native-client runtime, live backend
behavior, or live probes.

Signed Snapshot Consumer Contract v0 records future snapshot consumption
contracts, profile inventories, reference docs, validator, and tests under
`control/inventory/publication/`, `docs/reference/`, `scripts/`, and `tests/`.
No separate AIDE runtime report is needed; this is contract/design governance
and does not implement a snapshot reader runtime, relay, native client,
production signing, real signing keys, executable downloads, live backend
behavior, or live probes.

Native Client Contract v0 records future native client contracts, lane
inventories, readiness checklist, validator, and tests under
`control/inventory/publication/`, `docs/reference/`, `docs/operations/`,
`scripts/`, and `tests/`. No separate AIDE runtime report is needed; this is
contract/design governance and does not create Visual Studio/Xcode projects,
native GUI clients, FFI, installers, downloads, relay sidecars, live probes, or
Rust runtime wiring.

Native Client Project Readiness Review v0 records its committed audit/evidence
pack under `control/audits/native-client-project-readiness-v0/`, plus a
validator and tests under `scripts/` and `tests/`. No separate AIDE runtime
report is needed; this is readiness review only and does not create Visual
Studio/Xcode projects, native app source trees, GUI behavior, FFI, cache
runtime, downloads, installers, relay runtime, live probes, or runtime wiring.

Windows 7 WinForms Native Skeleton Planning v0 records its committed planning
pack under `control/audits/windows-7-winforms-native-skeleton-planning-v0/`,
plus a validator and tests under `scripts/` and `tests/`. No separate AIDE
runtime report is needed; this is planning only and does not create
`clients/`, Visual Studio solutions, C# projects, C# source, GUI behavior, FFI,
downloads, installers, cache runtime, telemetry, relay runtime, live probes, or
runtime wiring.

Relay Prototype Planning v0 records its committed planning pack under
`control/audits/relay-prototype-planning-v0/`, plus a validator and tests under
`scripts/` and `tests/`. No separate AIDE runtime report is needed; this is
planning only and does not implement a relay server, open sockets, add local
HTTP/FTP/SMB/AFP/NFS/WebDAV/Gopher behavior, expose private data, proxy a live
backend, enable live probes, or claim old-client relay support.

Post-Queue State Checkpoint v0 records its committed audit/reporting pack under
`control/audits/post-queue-state-checkpoint-v0/`. No separate AIDE runtime
report is needed; the pack is repo-governance evidence and does not add product
runtime behavior, deployment behavior, live probes, external observations,
production signing, relay services, or native clients.

Relay Surface Design v0 records its future relay inventory, architecture and
reference docs, security/privacy posture, unsigned operator checklist,
validator, and tests under `control/inventory/publication/`, `docs/`, and
`scripts/`. No separate AIDE runtime report is needed; this is design and
governance only and does not add a relay runtime, sockets, protocol servers,
private data exposure, write/admin routes, live-probe passthrough, native
sidecars, or production relay claims.

Rust Source Registry Parity Catch-up v0 records its Rust candidate update,
Python-oracle source-registry goldens, parity case map, stdlib checker, and
structure tests under `crates/eureka-core/`, `tests/parity/`, `tests/scripts/`,
and `scripts/`. No separate AIDE runtime report is needed; this is isolated
parity governance only and does not wire Rust into Python runtime, web, CLI,
HTTP API, workers, public-alpha paths, or production behavior.

Rust Local Index Parity Planning v0 records a planning-only parity lane under
`tests/parity/`, `tests/scripts/`, and `scripts/`. No separate AIDE runtime
report is needed; this adds a future parity plan, fixture map, acceptance
schema, validator, and tests only, with no Rust local-index implementation,
SQLite/indexing behavior, Python runtime replacement, or runtime/surface
wiring.

Full Project State Audit and Forward Plan v0 records its committed audit pack
under `control/audits/full-project-state-audit-v0/`, plus a validator and tests
under `scripts/` and `tests/`. No separate AIDE runtime report is needed; this
is audit/reporting governance only and does not add product runtime behavior,
relay runtime, native project scaffolding, live probes, deployment changes,
external observations, downloads, installers, local cache runtime, telemetry,
accounts, or cloud sync.

Public Data Contract Stability Review v0 records its committed audit pack under
`control/audits/public-data-contract-stability-review-v0/`, plus a stability
policy, validator, and tests under `docs/reference/`, `scripts/`, and `tests/`.
No separate AIDE runtime report is needed; this is contract-governance only and
does not add product runtime behavior, live APIs, deployment behavior, or a
production API stability claim.

Generated Artifact Drift Guard v0 records its generated-artifact inventory under
`control/inventory/generated_artifacts/`, operations doc, audit pack, checker,
and tests under `docs/operations/`,
`control/audits/generated-artifact-drift-guard-v0/`, `scripts/`, and `tests/`.
No separate AIDE runtime report is needed; this is validation/audit governance
only and does not regenerate artifacts by default, change runtime behavior,
deploy, call external services, open sockets, or claim production readiness.

Repository Shape Consolidation v0 records no separate AIDE runtime report. It
promotes `site/dist/` as the single generated static deployment artifact and
confirms `external/` as the outside-reference root through active docs,
inventories, validators, tests, and workflow metadata only.

Post-P49 Platform Audit v0 records its committed audit pack under
`control/audits/post-p49-platform-audit-v0/`, plus a validator and tests under
`scripts/` and `tests/`. No separate AIDE runtime report is needed; this is
audit/reporting governance only and does not add product runtime behavior,
hosted search, live probes, external observations, pack import, staging
runtime, AI runtime, deployment changes, downloads, uploads, accounts, or
master-index mutation.

Post-P50 Remediation Pack v0 records its committed audit pack under
`control/audits/post-p50-remediation-v0/`, plus a validator and tests under
`scripts/` and `tests/`. No separate AIDE runtime report is needed; this is
bounded remediation governance only and does not add hosted backend behavior,
live probes, source connectors, AI runtime, pack import, staging runtime,
external observations, downloads, uploads, accounts, or deployment-success
claims.

Static Deployment Evidence / GitHub Pages Repair v0 records its committed
audit pack under `control/audits/static-deployment-evidence-v0/`, plus a
validator and tests under `scripts/` and `tests/`. No separate AIDE runtime
report is needed; this is static deployment evidence governance only and does
not add backend hosting, public search hosting, live probes, source connectors,
credentials, telemetry, accounts, uploads, downloads, installers, or
deployment-success claims.

Public Search Production Contract v0 records its committed audit pack under
`control/audits/public-search-production-contract-v0/`, plus validator and
tests under `scripts/` and `tests/`. No separate AIDE runtime report is needed;
this is contract governance for the future hosted local-index wrapper only and
does not add backend hosting, live probes, source connectors, telemetry
runtime, accounts, uploads, downloads, installers, arbitrary URL fetching,
index mutation, AI runtime, or hosted-search claims.

Hosted Public Search Wrapper v0 records its committed audit pack under
`control/audits/hosted-public-search-wrapper-v0/`, plus wrapper, checker,
validator, docs, templates, and tests. No separate AIDE runtime report is
needed; this is local wrapper readiness and rehearsal only and does not deploy
a backend, verify hosted availability, enable live probes, downloads, uploads,
accounts, telemetry, arbitrary URL fetch, source connectors, AI runtime, index
mutation, pack import, or staging runtime.

Public Search Index Builder v0 records its committed audit pack under
`control/audits/public-search-index-builder-v0/`, plus builder, validator,
generated `data/public_index` artifacts, runtime integration, drift metadata,
docs, and tests. No separate AIDE runtime report is needed; this is controlled
local_index_only index generation only and does not add live source calls,
private local ingestion, executable payloads, downloads, uploads, arbitrary URL
fetching, AI runtime, pack import, staging runtime, master-index mutation, or
hosted deployment evidence.

Static Site Search Integration v0 records its committed audit pack under
`control/audits/static-site-search-integration-v0/`, plus generated no-JS
search surfaces, `data/search_config.json`, `data/public_index_summary.json`,
docs, validator, generated-artifact metadata, and tests. No separate AIDE
runtime report is needed; this is static publication integration only and does
not deploy a backend, configure a verified URL, enable live probes, add
downloads/uploads/accounts/telemetry, fetch arbitrary URLs, mutate indexes,
import packs, stage packs, or claim production search quality.

Public Search Safety Evidence v0 records its committed audit pack under
`control/audits/public-search-safety-evidence-v0/`, plus local evidence runner,
validator, docs, and tests. No separate AIDE runtime report is needed; this is
local/public-alpha safety evidence only and does not deploy a backend, enable
live probes, add downloads/uploads/installs/accounts/telemetry, fetch arbitrary
URLs, mutate indexes, or claim edge rate limits or production safety.
## P58 Hosted Public Search Rehearsal v0

The P58 report lives at
`control/audits/hosted-public-search-rehearsal-v0/hosted_public_search_rehearsal_report.json`.
It records localhost hosted-wrapper rehearsal only and does not claim a deployed
backend.

## P59 Query Observation Contract v0

The P59 report lives at `control/audits/query-observation-contract-v0/query_observation_contract_report.json`. It records query observation contract/schema/example validation only and does not claim telemetry, persistence, public query logging, cache mutation, miss-ledger mutation, probe enqueueing, index mutation, or hosted query intelligence runtime.

## P60 Shared Query/Result Cache v0

The P60 report lives at `control/audits/shared-query-result-cache-v0/shared_query_result_cache_report.json`. It records shared cache contract/schema/example validation only and does not claim runtime cache writes, persistent cache storage, telemetry, public query logging, miss-ledger mutation, search-need mutation, probe enqueueing, index mutation, or hosted query intelligence runtime.

## P61 Search Miss Ledger v0

The P61 report lives at `control/audits/search-miss-ledger-v0/search_miss_ledger_report.json`. It records search miss ledger contract/schema/example validation only and does not claim runtime ledger writes, persistent ledger storage, telemetry, public query logging, search-need creation, probe enqueueing, result-cache mutation, index mutation, or hosted query intelligence runtime.

## P62 Search Need Record v0

The P62 report lives at `control/audits/search-need-record-v0/search_need_record_report.json`. It records search need contract/schema/example validation only and does not claim runtime need storage, persistent need storage, telemetry, public query logging, demand-count runtime, probe enqueueing, candidate-index mutation, result-cache mutation, miss-ledger mutation, index mutation, or hosted query intelligence runtime.

## P63 Probe Queue v0

The P63 report lives at `control/audits/probe-queue-v0/probe_queue_report.json`. It records probe queue contract/schema/example validation only and does not claim queue runtime, persistent queue storage, telemetry, public query logging, probe execution, live source calls, source-cache mutation, evidence-ledger mutation, candidate-index mutation, index mutation, or hosted query intelligence runtime.

## P64 Candidate Index v0

The P64 report lives at `control/audits/candidate-index-v0/candidate_index_report.json`. It records candidate index contract/schema/example validation only and does not claim runtime candidate index, persistent candidate storage, telemetry, public query logging, public search candidate injection, candidate promotion runtime, source-cache mutation, evidence-ledger mutation, index mutation, or hosted query intelligence runtime.

## P65 Candidate Promotion Policy v0

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known absence page reporting is contract-only and points to `control/audits/known-absence-page-v0/known_absence_page_report.json`.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

P67 report: `control/audits/query-privacy-poisoning-guard-v0/query_privacy_poisoning_guard_report.json` records the contract-only guard posture, examples, validators, command evidence, blockers, and next branch P68.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## P68 Demand Dashboard v0

P68 report lives under `control/audits/demand-dashboard-v0/` and records synthetic aggregate-dashboard contract evidence only.

## P69 Source Sync Worker Contract v0

P69 report lives under `control/audits/source-sync-worker-contract-v0/` and records source sync worker contract evidence only.

## P70 Source Cache and Evidence Ledger v0

Report: `control/audits/source-cache-evidence-ledger-v0/source_cache_evidence_ledger_report.json`.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval Pack v0

The P71 audit pack is approval-only and records no connector execution, external calls, source cache mutation, evidence ledger mutation, or production readiness claim.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

Completed as an approval-only contract pack. It adds no Wayback/CDX/Memento connector runtime, no external calls, no archived content fetch, no capture replay, no WARC download, no public-query fanout, no telemetry, no credentials, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P73 GitHub Releases Connector Approval Pack v0.

<!-- P73-GITHUB-RELEASES-SUMMARY-START -->
## P73 GitHub Releases Connector Approval Pack v0

Completed as an approval-only release metadata connector pack. It adds no live GitHub connector runtime, no external calls, no GitHub API calls, no repository clone, no release fetch, no release asset download, no source archive download, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P74 PyPI Metadata Connector Approval Pack v0.
<!-- P73-GITHUB-RELEASES-SUMMARY-END -->

<!-- P74-PYPI-METADATA-SUMMARY-START -->
## P74 PyPI Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live PyPI connector runtime, no external calls, no PyPI API calls, no package metadata fetch, no release fetch, no wheel download, no sdist download, no package file download, no package install, no dependency resolution, no package archive inspection, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P75 npm Metadata Connector Approval Pack v0.
<!-- P74-PYPI-METADATA-SUMMARY-END -->

<!-- P75-NPM-METADATA-SUMMARY-START -->
## P75 npm Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live npm connector runtime, no external calls, no npm registry API calls, no npm/yarn/pnpm CLI calls, no package metadata fetch, no version fetch, no dist-tag fetch, no tarball metadata fetch, no tarball download, no package file download, no package install, no dependency resolution, no package archive inspection, no lifecycle script execution, no npm audit, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires package identity review, scoped package review, dependency metadata caution, lifecycle script risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P76 Software Heritage Connector Approval Pack v0.
<!-- P75-NPM-METADATA-SUMMARY-END -->

<!-- P76-SOFTWARE-HERITAGE-SUMMARY-START -->
## P76 Software Heritage Connector Approval Pack v0

Completed as an approval-only software identity/archive metadata connector pack. It adds no live Software Heritage connector runtime, no external calls, no Software Heritage API calls, no SWHID resolution, no origin/visit/snapshot/release/revision/directory/content lookup, no source code download, no repository clone, no source archive download, no source file retrieval, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires SWHID/origin/repository identity review, source-code-content risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P77 Public Hosted Deployment Evidence v0.
<!-- P76-SOFTWARE-HERITAGE-SUMMARY-END -->

<!-- P77-PUBLIC-HOSTED-DEPLOYMENT-EVIDENCE-START -->
## P77 Public Hosted Deployment Evidence v0

Completed as evidence-only deployment review. It adds no deployment, provider mutation, DNS changes, credentials, live source calls, hosted backend runtime, telemetry, accounts, downloads, uploads, or index/cache/ledger mutation. The configured GitHub Pages URL returned 404 for required routes, and no hosted backend URL is configured. Next recommended branch: P78 External Baseline Comparison Report v0 after Manual Batch 0, or P79 Object Page Contract v0 if the manual batch remains pending.
<!-- P77-PUBLIC-HOSTED-DEPLOYMENT-EVIDENCE-END -->

<!-- P78-EXTERNAL-BASELINE-COMPARISON-START -->
## P78 External Baseline Comparison Report v0

P78 added local-only comparison readiness for manual external baselines. Current eligibility is `no_observations`: Batch 0 has 0 observed records and 39 pending slots. No web calls, source API calls, model calls, fabricated observations, fabricated comparisons, production readiness claim, or index/cache/ledger/candidate/master-index mutation were made. Codex-safe next branch is P79 Object Page Contract v0 while Manual Observation Batch 0 remains human-operated.
<!-- P78-EXTERNAL-BASELINE-COMPARISON-END -->

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0

The P79 report is in `control/audits/object-page-contract-v0/`. It is evidence-first and contract-only; it adds no runtime object-page generation.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Commands:

- `python scripts/validate_source_page.py --all-examples`
- `python scripts/validate_source_page.py --all-examples --json`
- `python scripts/validate_source_page_contract.py`
- `python scripts/validate_source_page_contract.py --json`
- `python scripts/dry_run_source_page.py --source-id internet-archive-placeholder --source-family internet_archive --json`

These are contract-only/source-page governance checks. They make no network calls, implement no runtime source pages, execute no source sync worker, enable no connector, mutate no cache/ledger/index, and enable no downloads, installs, or execution.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->

<!-- P81-COMPARISON-PAGE-CONTRACT-START -->
## P81 Comparison Page Contract v0

P81 reports comparison-page governance only. The validation commands are stdlib-only and local-only, and comparison pages remain future runtime work.
<!-- P81-COMPARISON-PAGE-CONTRACT-END -->

<!-- P82-CROSS-SOURCE-IDENTITY-RESOLUTION-START -->
## P82 Cross-Source Identity Resolution Contract v0

P82 reports identity-resolution governance only. Validation is stdlib-only and local-only; runtime identity resolution remains future work.
<!-- P82-CROSS-SOURCE-IDENTITY-RESOLUTION-END -->

<!-- P83-RESULT-MERGE-DEDUPLICATION-START -->
## P83 Result Merge and Deduplication Contract v0

Report: `control/audits/result-merge-deduplication-contract-v0/result_merge_deduplication_report.json`.
<!-- P83-RESULT-MERGE-DEDUPLICATION-END -->

<!-- P84-EVIDENCE-WEIGHTED-RANKING-START -->
## P84 Evidence-Weighted Ranking Contract v0

Report: `control/audits/evidence-weighted-ranking-contract-v0/evidence_weighted_ranking_report.json`.
<!-- P84-EVIDENCE-WEIGHTED-RANKING-END -->

<!-- P85-COMPATIBILITY-AWARE-RANKING-START -->
## P85 Compatibility-Aware Ranking Contract v0

Audit pack: `control/audits/compatibility-aware-ranking-contract-v0/`.
<!-- P85-COMPATIBILITY-AWARE-RANKING-END -->

<!-- P86-PUBLIC-QUERY-OBSERVATION-RUNTIME-PLAN-START -->
## P86 Public Query Observation Runtime Planning v0

Audit report: `control/audits/public-query-observation-runtime-planning-v0/public_query_observation_runtime_planning_report.json`.
<!-- P86-PUBLIC-QUERY-OBSERVATION-RUNTIME-PLAN-END -->

<!-- P87-IA-METADATA-CONNECTOR-RUNTIME-PLAN-START -->
## P87 Internet Archive Metadata Connector Runtime Planning v0

Audit report: `control/audits/internet-archive-metadata-connector-runtime-planning-v0/internet_archive_metadata_connector_runtime_planning_report.json`.
<!-- P87-IA-METADATA-CONNECTOR-RUNTIME-PLAN-END -->

<!-- P88-WAYBACK-CDX-MEMENTO-CONNECTOR-RUNTIME-PLAN-START -->
## P88 Wayback/CDX/Memento Connector Runtime Planning v0

Audit report: `control/audits/wayback-cdx-memento-connector-runtime-planning-v0/wayback_cdx_memento_connector_runtime_planning_report.json`.
<!-- P88-WAYBACK-CDX-MEMENTO-CONNECTOR-RUNTIME-PLAN-END -->

<!-- P89-GITHUB-RELEASES-CONNECTOR-RUNTIME-PLAN-START -->
## P89 GitHub Releases Connector Runtime Planning v0

Audit report: `control/audits/github-releases-connector-runtime-planning-v0/github_releases_connector_runtime_planning_report.json`.
<!-- P89-GITHUB-RELEASES-CONNECTOR-RUNTIME-PLAN-END -->

<!-- P90-PYPI-METADATA-CONNECTOR-RUNTIME-PLAN-START -->
## P90 PyPI Metadata Connector Runtime Planning v0

Audit report: `control/audits/pypi-metadata-connector-runtime-planning-v0/pypi_metadata_connector_runtime_planning_report.json`.
<!-- P90-PYPI-METADATA-CONNECTOR-RUNTIME-PLAN-END -->

<!-- P91-NPM-METADATA-CONNECTOR-RUNTIME-PLAN-START -->
## P91 npm Metadata Connector Runtime Planning v0

Audit report: `control/audits/npm-metadata-connector-runtime-planning-v0/npm_metadata_connector_runtime_planning_report.json`.
<!-- P91-NPM-METADATA-CONNECTOR-RUNTIME-PLAN-END -->

## P92 Software Heritage Connector Runtime Planning v0

Audit report: `control/audits/software-heritage-connector-runtime-planning-v0/software_heritage_connector_runtime_planning_report.json`.

Planning-only and approval-gated. The runtime remains blocked because P76 keeps connector approval pending.

## P93 Object/Source/Comparison Page Runtime Planning v0

Audit report: `control/audits/object-source-comparison-page-runtime-planning-v0/object_source_comparison_page_runtime_planning_report.json`.

Planning-only and read-only page runtime plan. Local dry-run work requires operator approval; hosted runtime remains blocked by deployment evidence.

<!-- P94-PACK-IMPORT-RUNTIME-PLAN-START -->
## P94 Pack Import Runtime Planning v0

Added planning-only pack import runtime audit metadata. The runtime remains unimplemented and disabled; no packs are imported or staged, no pack content is executed, no URLs are followed, no public contribution intake is enabled, and no indexes/cache/ledger/candidates are mutated.
<!-- P94-PACK-IMPORT-RUNTIME-PLAN-END -->
