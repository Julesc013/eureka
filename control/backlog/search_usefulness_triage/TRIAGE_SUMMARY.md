# Triage Summary

Search Usefulness Backlog Triage v0 selects the next usefulness wedge from current audit evidence. It is a planning and governance pack only; no runtime behavior, source connector, Rust behavior, app work, or deployment posture is changed here.

## Current Audit State

The Search Usefulness Audit v0 runner was re-run for this triage. Current local results:

| Metric | Count |
| --- | ---: |
| Total queries | 64 |
| Covered | 5 |
| Partial | 1 |
| Source gap | 43 |
| Capability gap | 13 |
| Unknown | 2 |
| Google pending manual observations | 64 |
| Internet Archive metadata pending manual observations | 64 |
| Internet Archive full text/OCR pending manual observations | 64 |

Top failure modes:

| Failure mode | Count |
| --- | ---: |
| source_coverage_gap | 49 |
| query_interpretation_gap | 46 |
| planner_gap | 45 |
| compatibility_evidence_gap | 25 |
| representation_gap | 14 |
| decomposition_gap | 12 |
| member_access_gap | 12 |
| identity_cluster_gap | 11 |

The data says Eureka's current bottleneck is not architecture theater. It is missing governed source coverage, missing source capability depth, incomplete planner interpretation for old platform intent, and missing member/compatibility evidence.

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

1. Source coverage and capability depth are underspecified. Current active sources are synthetic fixtures and recorded GitHub Releases fixtures only.
2. Placeholder/future sources remain Internet Archive, Wayback/Memento, Software Heritage, and local files; they must not be described as implemented connectors.
3. Planner coverage does not yet capture enough old OS aliases, latest-compatible release intent, vague identity clues, or app-vs-OS-media suppression.
4. Member-level discovery is bounded to current synthetic fixture behavior and does not yet provide broad member target refs, parent lineage, or member-level index records.
5. Compatibility evidence is too thin for Windows 98, Windows 2000, Windows XP, Vista, and Windows 7 / NT 6.1 claims.

## Why Live Crawling Is Deferred

Live crawling would hide the current evidence problem behind unstable coverage. Recorded fixtures and a source capability model come first so the repo can prove what a source can answer, what evidence it carries, and how a query status changes without fabricating external results.

## Why Rust Parity Is Not Immediate

Rust Query Planner parity is useful after Python planner behavior has the right shape. Porting current planner gaps too early would freeze weakness rather than preserve useful behavior. Python remains the oracle, and Rust remains parity-first.

## Why Native Apps Are Deferred

Native apps would mostly repackage current usefulness gaps. The next value comes from better source coverage, planner interpretation, member discovery, and compatibility evidence in the backend reference lane.

## Exact Next Milestone

Immediate next milestone at triage time: Source Coverage and Capability Model v0.

This should define source-family capability fields, coverage-depth vocabulary, fixture expectations, and tests that prevent placeholder sources from being promoted silently.

Implementation note: Source Coverage and Capability Model v0 is now in place
as bounded source-registry metadata plus public projection. It does not add
connectors, live probing, crawling, or source acquisition behavior. The next
implementation milestone is Real Source Coverage Pack v0 with recorded
fixtures only.

## Evidence That Would Change The Plan

The plan should be revisited if:

- a recorded source pack makes old-platform queries less dominant than another family
- manual external baseline observations show a different high-value wedge
- member-level discovery becomes blocked by a contract problem that must be solved first
- hardening tests reveal route/public-alpha/privacy constraints that prevent safe fixture work

Until then, source capability modeling is the lowest-risk next move with the highest future leverage.
