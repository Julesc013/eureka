# Public Search Result Card Contract v0

Status: implemented as a contract reference and used by Local Public Search Runtime v0.

Public Search Result Card Contract v0 defines the public result-card envelope
for Eureka search displays and JSON responses. The card is the unit that local
`/search` HTML and `/api/v1/search` JSON now emit in Local Public Search Runtime
v0, and that lite/text surfaces, native clients, relay clients, snapshot
consumers, and contribution/review tooling may consume after their own contracts
allow it.

This contract does not make public search hosted, does not add static search
handoff, does not enable live probes, and does not enable downloads, installers,
execution, uploads, or local path search. It does not claim production ranking
quality, production API stability, malware safety, rights clearance, or
production readiness.

In short: the result card is not a production ranking guarantee, must not claim
malware safety, must not claim rights clearance, and prepared the safety
milestone, Public Search Safety / Abuse Guard v0, rather than replacing it.
Public Search Safety / Abuse Guard v0 is now implemented as guardrails, and
Local Public Search Runtime v0 uses those guardrails for local/prototype result
cards. Hosted public exposure still waits for later rehearsal and operator
approval.

## Contract Files

- Schema: `contracts/api/search_result_card.v0.json`
- Examples: `contracts/api/examples/search_result_card_*.v0.json`
- API response alignment: `contracts/api/search_response.v0.json`
- Audit pack: `control/audits/public-search-result-card-contract-v0/`

## Required Card Shape

Every public result card must contain:

- `schema_version` and `contract_id`
- `stability`
- `result_id`, `title`, and `record_kind`
- `result_lane`
- `user_cost`
- `source`
- `identity`
- `evidence`
- `compatibility`
- `actions`
- `rights`
- `risk`
- `warnings`
- `limitations`
- `gaps`

Optional blocks include `subtitle`, `summary`, `matched_query_terms`,
`why_matched`, `why_ranked`, `parent_lineage`, `member`, `representation`,
`temporal`, `links`, and `debug`. Optional blocks must remain public-safe and
must not leak private paths, raw source payloads, credentials, local store roots,
or live fetch locators.

## Lanes And User Cost

`result_lane` uses the bounded vocabulary already aligned with the engine:

- `best_direct_answer`
- `installable_or_usable_now`
- `inside_bundles`
- `official`
- `preservation`
- `community`
- `documentation`
- `mentions_or_traces`
- `absence_or_next_steps`
- `still_searching`
- `other`

`user_cost.score` is an integer from 0 through 9. Lower scores mean less user
detective work. The score is a deterministic stable-draft hint, not a
production ranking guarantee. Cards must include `user_cost.reasons` so old and
text clients can explain the score without rich UI.

## Source And Identity

The `source` block identifies the public source family, coverage depth, source
posture, and whether the source was checked as a local index, recorded fixture,
static summary, future live probe, or not checked. In v0, future live probe is a
label for future contracts only; it does not enable live probes.

The `identity` block carries a public-safe target reference plus optional
resource, representation, member, native, object, or state identifiers.
Identity status is explicit: exact, candidate, ambiguous, unresolved,
synthetic_member, article_segment, or unknown. Private local paths and internal
database row ids are not public identity.

## Evidence And Compatibility

The `evidence` block carries public-safe summaries, counts, provenance notes,
and missing-evidence notes. It must not include raw source payloads by default.

The `compatibility` block carries status, target platforms, architecture,
evidence summaries, confidence, caveats, and unknowns. It must not claim
universal compatibility. Compatibility status is a public signal, not proof that
an artifact has been tested on every platform.

## Parent, Member, And Representation

Cards support smallest-actionable-unit behavior through `member`,
`parent_lineage`, and `representation`. A member result may explain that a small
driver, article segment, file, or documentation member is more useful than the
larger bundle that contains it.

Representation fields describe public-safe representation metadata such as kind,
media type, file name, size, checksum, and limitations. They do not expose
private local paths or executable handoff URLs.

## Actions

Actions are split into `allowed`, `blocked`, and `future_gated`.

Allowed v0 concepts are read-only or inspection-oriented:

- `inspect`
- `preview`
- `read`
- `cite`
- `export_manifest`
- `view_provenance`
- `compare`
- `view_source`
- `view_absence_report`

Blocked or future-gated concepts include:

- `download`
- `download_member`
- `mirror`
- `install_handoff`
- `package_manager_handoff`
- `emulator_handoff`
- `vm_handoff`
- `execute`
- `live_probe`
- `restore_apply`
- `uninstall`
- `rollback`
- `upload`
- `submit_private_source`

Every action entry has an `action_id`, `status`, `reason`, optional
`policy_reference`, and optional future-policy/confirmation flags. A future
runtime must not treat a future-gated action as enabled.

## Rights And Risk

The `rights` block records public metadata posture, source-term caveats,
restricted/review-required states, or unknown rights status. It must not claim
rights clearance. `distribution_allowed: "unknown"` is not permission.

The `risk` block records executable-risk posture and malware-scan status. It
must not claim malware safety. In v0, executable artifacts are not made
downloadable or executable through a result card.

## Warnings, Limitations, And Gaps

Warnings have a type, message, and severity: `info`, `caution`, `warning`, or
`blocked`.

Common limitations include fixture-backed evidence, limited source coverage,
limited compatibility evidence, no live probe, no download, no install, no
execute, no upload, no malware scan, no rights clearance, external-baseline
pending, static summary only, local-index-only, and not production ranking.

Gaps explain bounded absence and next actions. A card may say that the local
index did not find a result, but it must not imply that the live web or external
archives were checked.

## Field Stability

The field matrix in
`control/audits/public-search-result-card-contract-v0/RESULT_CARD_FIELD_MATRIX.md`
classifies fields as stable-draft, experimental, volatile, internal, or future.
Stable-draft fields are intended for old-client and future-runtime continuity.
Experimental fields may change before a runtime implementation. Internal fields
are forbidden from public cards.

## Old-Client Rendering

Lite HTML and text clients should render at least title, lane, user-cost score
and label, source id/family, public target ref, first evidence summary, allowed
inspect/read actions, blocked unsafe actions, warnings, and limitations. They
should degrade by dropping rich panels first, not by hiding source, uncertainty,
or safety posture.

## Relationship To Other Contracts

Public Search API Contract v0 uses this card as the canonical shape for
`results[]` in `contracts/api/search_response.v0.json`. The API contract remains
contract-only.

The Action Download Install Policy governs blocked and future-gated actions.
Executable Risk Policy governs executable-risk caveats. Rights and Access Policy
governs rights caveats. Native, relay, and snapshot contracts may reference this
card as a future input shape, but this milestone does not implement native
clients, relay runtime, or snapshot reader runtime.

Future reviewed evidence packs may supply public-safe evidence summaries,
source locators, compatibility caveats, member notes, and absence notes for
result cards. Evidence Pack Contract v0 does not import those packs, make claims
canonical, or change current local public search runtime behavior.
Future reviewed index packs may supply public-safe coverage and record-summary
metadata for result cards. Index Pack Contract v0 does not import or merge
those packs, export raw databases or caches, make summaries canonical proof, or
change current local public search runtime behavior.
Future reviewed contribution packs may supply accepted public deltas or review
notes for result cards only after Master Index Review Queue Contract v0-governed
review. Contribution Pack Contract v0 does not upload, import, moderate,
accept, or make contributed records canonical proof, and it does not change
current local public search runtime behavior.
Source/Evidence/Index Pack Import Planning v0 does not change result cards.
Future validated or quarantined packs remain local claims/candidates and must
not appear in public result cards until a later explicit local-index or
master-index review milestone permits reviewed public output.
AI Provider Contract v0 does not add AI result cards or generated snippets.
Future AI explanations may appear only as typed, review-required suggestions
after separate output validation and public-search contract updates. They are
not canonical truth, rights clearance, malware safety, or ranking authority.
Typed AI Output Validator v0 adds that offline output validation step through
`scripts/validate_ai_output.py`, but it does not display AI output on result
cards, import AI output into evidence/contribution packs, or alter ranking.
Pack Import Report Format v0 may record future validation outcomes for packs
or typed AI output bundles before reviewed public records exist. It does not
change result-card fields, import packs, stage packs, mutate local indexes,
upload, or mutate public search or the master index.

Public Search Index Builder v0 projects the controlled generated public index
documents back into this result-card shape for the local/prototype public-search
runtime. Each generated document carries source, evidence, compatibility,
action, warning, and limitation summaries; blocked actions still include
download, install handoff, execute, and upload. The generated index does not
prove source truth, rights clearance, malware safety, production ranking
quality, or hosted availability.

## Runtime Preconditions

Local Public Search Runtime v0 emits public result cards after satisfying the
implemented Public Search Safety / Abuse Guard v0 policy, local index
ownership, public route validation, bounded query/result limits,
no-live-probe enforcement, action-policy enforcement, and tests proving no
downloads, installers, execution, uploads, arbitrary URL fetch, local path
search, private data exposure, malware-safety claim, rights-clearance claim, or
production API claim was added by accident.

Hosted public exposure must still pass the runtime readiness checklist at
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`; this checklist
does not approve hosted deployment by itself.
Public Search Rehearsal v0 now records local/prototype evidence that emitted
cards remain aligned with this contract for representative safe queries and
absence cases. It adds no hosted backend, live probes, downloads, installers,
uploads, execution, malware-safety claim, rights-clearance claim, telemetry, or
production ranking guarantee.

Public Search Safety Evidence v0 adds a broader pre-hosted safety check. It
verifies local result-card safety shape for safe public-search queries while
downloads, installs, execution, uploads, live probes, and local path access
remain blocked or disabled.

## Out Of Scope

This contract and local runtime do not implement hosted backend deployment,
live source probes, Internet Archive calls, Google
queries, arbitrary URL fetch, crawling, downloads, installers, uploads,
accounts, telemetry, native clients, relay runtime, snapshot reader runtime,
TLS, auth, rate limiting, process management, custom domains, production API
stability, or production readiness.
## P58 Rehearsal Alignment

P58 safe-query checks verify that local hosted search responses still expose
result-card safety shape, including source, evidence, compatibility, warnings,
limitations, and blocked dangerous actions.
## Query Observation Boundary

P59 Query Observation Contract v0 records only summary-level result posture for
future query intelligence. It does not copy result cards into a result cache,
does not publish query observations, and does not mutate candidate, local, or
master indexes.

## Shared Result Cache Boundary

P60 Shared Query/Result Cache v0 may summarize public-safe result-card fields
for future reuse. A cache entry is not the full result card, not source
evidence, not a download/install promise, not telemetry, and not master-index
truth.

## Search Miss Ledger Boundary

P61 Search Miss Ledger v0 may reference public-safe result-card summaries as
weak hits or near misses. A miss entry is not the full result card, not source
evidence, not a search need, not a probe job, not telemetry, and not
master-index truth.

## Search Need Record Boundary

P62 Search Need Record v0 may reference public-safe result-card summaries as
context for a scoped unresolved need. A need record is not the full result card,
not source evidence, not a probe job, not a candidate record, not telemetry, and
not master-index truth.

## Probe Queue Boundary

P63 Probe Queue v0 may reference public-safe result-card context only through
query observation, cache, miss, or search-need refs. A probe queue item is not
the full result card, not source evidence, not probe execution, not a candidate
record, not telemetry, and not master-index truth.
## P64 Candidate Index Note

Result cards are not candidate records. P64 candidate examples are provisional
contract artifacts and do not become public result cards, public action
targets, evidence acceptance, or master-index records.

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

Future result cards may cite reviewed source cache or evidence ledger references, but P70 is contract-only and does not surface ledger records, alter ranking, or mutate public search behavior.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
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

## P77 Deployment Boundary

Result-card contracts remain local/public-index contracts only. P77 adds no hosted backend claim, download action, external-source fanout, telemetry, or index mutation.

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
