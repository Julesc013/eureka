# Known Absence Page Contract v0

Known Absence Page v0 defines a future public-safe explanation envelope for unresolved searches. Scoped absence, not global absence, is the governing rule: a page may describe what Eureka checked, what was not checked, why a verified result was not found, and what safe next actions may exist.

A known absence page is not a runtime page yet. A known absence page is not evidence acceptance. A known absence page is not candidate promotion. A known absence page is not master-index mutation.

## Page Shape

The contract records query context, an absence summary, checked and not-checked scope, near misses, weak hits, gap explanations, source status, evidence context, candidate context, safe next actions, user-facing sections, an API projection, a static projection, privacy, rights/risk, limitations, and hard no-global-absence/no-mutation guarantees.

## Checked Scope

Checked scope lists the specific indexes, source families, capabilities, and snapshot refs used by the explanation. Not-checked scope lists sources, source families, capabilities, and reasons not checked. The page must never imply an exhaustive search.

## Near Misses And Gaps

Near misses and weak hits are public-safe summaries only. They do not embed raw result payloads and do not become verified results. Gap explanations name source coverage, capability, compatibility evidence, member access, representation, query interpretation, live-probe-disabled, external-baseline, deep-extraction, OCR, source-cache, or policy limits.

## Safe Actions

No download/install/upload/live fetch action is enabled by P66. Informational actions such as refining the query, viewing near misses, or viewing checked sources may be enabled in examples. Future actions such as manual observation, source/evidence pack submission, search need creation, probe queueing, live probes, deep extraction, or OCR remain future-only and require approval where applicable.

## API And Static Projection

The API projection is a contract model for a future `known_absence_response` compatible with search responses. It is not runtime API implementation. The static projection documents how a no-JS demo could be rendered, but P66 does not generate a static artifact.

## Privacy Rights And Risk

Raw query retention defaults to none. Public-safe examples must not contain raw private queries, private paths, secrets, private URLs, account identifiers, IP addresses, or private local result identifiers. Rights clearance and malware safety are not claimed.

## Relations

Known absence pages can reference query observations, shared result cache entries, miss ledger entries, search needs, probe queue items, candidate records, and promotion-policy context. These references are explanatory only and do not create, update, or promote those records.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Query privacy and poisoning guard decisions are a future contract-only input for known absence pages. A known absence explanation should only use public-safe, privacy-filtered, poisoning-checked query context and must not let fake demand, source-stuffing, candidate-poisoning, private paths, secrets, IP addresses, account IDs, or private URLs into public aggregate learning. P67 does not create runtime known absence pages.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.

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
