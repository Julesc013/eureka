# Source Page Contract v0

Source Page Contract v0 is a contract-only, evidence-first page contract for future public source pages. A source page explains what a source is, what Eureka currently knows about it, what coverage exists, what connector posture applies, what policy gates block live use, and how users should interpret results from that source.

A source page is not runtime yet. Source page is not connector runtime, source page is not source trust authority, not a source API proxy, not a scraper, not a mirror, not a rights clearance page, not a malware safety page, and not a production monitoring dashboard.

Boundary rules:

- No live source calls.
- No source cache mutation.
- No evidence ledger mutation.
- No candidate promotion.
- No public index mutation, local index mutation, no master index mutation.
- No download, no mirror, no install, no execution, no upload, and no arbitrary URL fetch.
- No rights clearance, no malware safety, and no authoritative source trust claim.

## Source Identity, Family, And Status

`source_identity` records `source_id`, `source_family`, labels, inventory refs, connector refs, and identity status. Allowed source families include Internet Archive, Wayback/CDX/Memento, GitHub Releases, PyPI, npm, Software Heritage, local fixture, recorded fixture, source pack, evidence pack, placeholder, and unknown. Public examples do not include live URLs unless they are already public-safe repo refs, and no homepage is fetched.

`source_status` distinguishes `active_fixture`, `active_recorded_fixture`, `placeholder`, `future`, `approval_required`, `disabled`, `local_private_future`, and `unknown`. It records whether live support, live enablement, connector approval, connector runtime, source cache runtime, evidence ledger runtime, public search fanout, and public index inclusion apply. P80 examples keep live support and live enablement false.

## Coverage

`coverage` records bounded coverage depth: none, placeholder, fixture-only, recorded fixture, future metadata summary, future source cache, future evidence ledger, or unknown. `source_coverage_claim_not_exhaustive` must be true. Source pages must describe coverage limitations and should not imply complete coverage.

## Connector And Source Policy

`connector_posture` records whether there is no connector, a fixture-only path, a future approval-required connector, a disabled connector, or an unknown posture. Connector approval refs may point to P71-P76 approval packs, but those packs are not runtime health evidence.

`source_policy` records source terms, automated access, rights/access, privacy, and risk review posture. Official source policy review, User-Agent/contact decisions, rate limits, timeouts, retry/backoff, and circuit breakers remain required before any future live connector planning.

## Cache, Evidence, Search, And Query Intelligence

Source pages project future source cache and evidence ledger state but cannot mutate either. They may eventually describe reviewed source cache records and evidence ledger observations. Public search remains local_index_only and must not fan out live to source pages or connectors.

Public index and public search projection are descriptive. Source badges and source filters are future integrations. Query intelligence projections may reference future search needs, probe queue items, demand dashboard summaries, known absence records, and candidates, but source pages cannot mutate query-intelligence records.

## Gaps, Trust, Rights, And Risk

Source pages record source coverage gaps, connector approval gaps, source policy review gaps, live probe disabled gaps, source cache missing, evidence ledger missing, compatibility evidence gaps, member access gaps, representation gaps, external baseline pending, and manual observation pending gaps.

Source pages preserve source disagreement and provenance caution. They do not claim source trust, source authority, source completeness, rights clearance, malware safety, or production readiness.

Allowed actions are inspect source metadata, view limitations, view related results, view evidence, and cite source page. Disabled actions are live probe, download, mirror, install, execute, upload, and arbitrary URL fetch.

## Projections

Result-card/source-badge projection is contract-only and future-only. API projection reserves `/source/{source_id}` and `/api/v1/source/{source_id}` as future routes with `implemented_now: false`. Static projection is future-only in P80; no static source page demo artifact is generated.

## Relationships

Source pages explain source posture for object pages, public search, public index, source sync workers, source cache, evidence ledger, connector approval packs, candidate index, candidate promotion policy, known absence pages, and future comparison pages. Source pages are not source sync workers and cannot execute source sync jobs.

## Deferred

Runtime source pages, persistent page storage, source-page links in public search, source badge rendering, source sync execution, source cache runtime, evidence ledger runtime, connector runtime, and hosted source-page routes remain future work.

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
