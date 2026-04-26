# Triage Summary

Search Usefulness Backlog Triage v0 selects the next usefulness wedge from current audit evidence. It is a planning and governance pack only; no runtime behavior, source connector, Rust behavior, app work, or deployment posture is changed here.

## Current Audit State

The Search Usefulness Audit v0 runner was re-run for this triage. Current local results:

| Metric | Count |
| --- | ---: |
| Total queries | 64 |
| Covered | 5 |
| Partial | 4 |
| Source gap | 41 |
| Capability gap | 12 |
| Unknown | 2 |
| Google pending manual observations | 64 |
| Internet Archive metadata pending manual observations | 64 |
| Internet Archive full text/OCR pending manual observations | 64 |

Top failure modes:

| Failure mode | Count |
| --- | ---: |
| source_coverage_gap | 49 |
| compatibility_evidence_gap | 25 |
| planner_gap | 24 |
| query_interpretation_gap | 21 |
| representation_gap | 14 |
| decomposition_gap | 12 |
| member_access_gap | 12 |
| identity_cluster_gap | 11 |

The data says Eureka's current bottleneck is not architecture theater. Source coverage is still dominant, but Old-Platform Software Planner Pack v0 reduced the planner/query-interpretation counts by making old-platform intent deterministic. The next visible gaps are member/representation depth, compatibility evidence, and further recorded source coverage.

## Selected Wedges

Primary wedge: old-platform-compatible software search.

Secondary wedge: member-level discovery inside bundles.

These wedges are selected because they cover many high-value hard queries while staying true to the temporal object resolver doctrine:

- return a specific software product/release/driver/tool rather than a noisy parent collection
- preserve platform and compatibility evidence
- expose representation/access paths and possible direct artifacts
- explain absence when the current corpus cannot satisfy the query
- demote parent containers when an inner member is the useful unit

## Top Blockers

1. Source coverage is still narrow even after recorded Internet Archive-like and local bundle fixtures.
2. Placeholder/future sources remain Internet Archive live, Wayback/Memento, Software Heritage, and local files; they must not be described as implemented connectors.
3. Member-level discovery is now bounded to committed fixture members and needs broader recorded source/member coverage before it can answer many real queries.
4. Compatibility evidence now exists for current fixture-backed old-platform signals, but Windows 98/95, Vista-depth evidence, broader architecture coverage, and real release-note/source coverage remain thin.
5. Result lanes and user-cost hints exist as bounded annotations, but the project has not yet measured their before/after usefulness delta.

## Why Live Crawling Is Deferred

Live crawling would hide the current evidence problem behind unstable coverage. Recorded fixtures and a source capability model come first so the repo can prove what a source can answer, what evidence it carries, and how a query status changes without fabricating external results.

## Why Rust Parity Is Not Immediate

Rust Query Planner parity is useful after Python planner behavior has the right shape. Porting current planner gaps too early would freeze weakness rather than preserve useful behavior. Python remains the oracle, and Rust remains parity-first.

## Why Native Apps Are Deferred

Native apps would mostly repackage current usefulness gaps. The next value comes from better source coverage, planner interpretation, member discovery, and compatibility evidence in the backend reference lane.

## Exact Next Milestone

Immediate next milestone at triage time: Source Coverage and Capability Model v0.

That milestone and Real Source Coverage Pack v0 are now implemented. Source
Coverage and Capability Model v0 defined source-family capability fields,
coverage-depth vocabulary, fixture expectations, and tests that prevent
placeholder sources from being promoted silently. Real Source Coverage Pack v0
then added recorded Internet Archive-like fixtures plus local bundle fixtures
without live probing, crawling, scraping, or arbitrary local filesystem
ingestion. Old-Platform Software Planner Pack v0 then added deterministic OS
aliases, latest-compatible release intent, driver/hardware/OS intent, vague
identity uncertainty, documentation intent, member-discovery hints, and
app-vs-OS-media suppression hints without adding ranking, fuzzy/vector
retrieval, LLM planning, live source behavior, or connector work. Member-Level
Synthetic Records v0 then added deterministic member target refs and parent
lineage for bounded local bundle fixtures. Result Lanes + User-Cost Ranking v0
then added bounded deterministic lane and user-cost explanations without adding
production ranking, fuzzy/vector retrieval, LLM scoring, live source behavior,
or connector work. Compatibility Evidence Pack v0 then added compact
source-backed compatibility evidence from committed fixture metadata, member
paths, README text, and compatibility notes while keeping unknown compatibility
valid and avoiding installer execution, live source behavior, scraping, and
compatibility-oracle claims.

Current next implementation milestone: Search Usefulness Audit Delta v0.

## Evidence That Would Change The Plan

The plan should be revisited if:

- a recorded source pack makes old-platform queries less dominant than another family
- manual external baseline observations show a different high-value wedge
- the compatibility evidence model proves too thin to explain status changes in
  the audit delta
- hardening tests reveal route/public-alpha/privacy constraints that prevent safe fixture work

Until then, an audit delta is the lowest-risk next move because source,
planner, member, lane/cost, and compatibility-evidence v0 seams now exist and
should be measured before the next source or surface implementation slice.
