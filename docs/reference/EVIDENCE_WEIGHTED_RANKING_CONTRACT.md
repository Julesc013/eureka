# Evidence-Weighted Ranking Contract v0

Evidence-weighted ranking is a contract-only future presentation layer for explaining how Eureka may later order public search results, result groups, object-page projections, source-page projections, and comparison candidates by evidence quality, provenance strength, source posture, freshness, conflict state, action safety, rights/risk caution, and gap transparency.

Ranking is not runtime yet. Ranking is not truth. Ranking is not candidate promotion. Ranking is not source trust. Ranking is not popularity/telemetry/ad/user-profile ranking. P84 does not change current public search ordering, does not suppress results, does not hide weak or conflicting results, and does not mutate source cache, evidence ledger, candidate index, public index, local index, runtime index, or master index.

## Evidence Strength

The evidence strength model classifies evidence as none, weak, medium, strong, conflicting, or unknown. Name match alone is weak. Intrinsic identifiers, checksums, compatibility evidence, source-backed metadata, and reviewed provenance are stronger, but evidence strength is not truth.

## Provenance And Source Posture

The provenance strength model records fixture, recorded fixture, source pack, evidence pack, source-cache future, evidence-ledger future, and manual-review future bases. Provenance is not truth. Source posture records active fixture, recorded fixture, approval-required, placeholder, disabled, or unknown states. Source prestige alone is not evidence and source_trust_claimed remains false.

## Freshness And Staleness

Freshness and staleness are explanatory factors only in v0. Freshness_score_applied_now is false, and current runtime order is preserved.

## Conflict And Uncertainty

Conflicts must not be hidden. Conflict may become a future penalty with visible explanation, but conflict_suppresses_result_now is false. Uncertainty explanation is required, and weak/conflicting results remain visible.

## Candidate And Gap Handling

Candidate confidence is not truth. Candidate-only or review-required records can be labelled provisional, but candidate_promotion_performed is false. Absence/gap transparency is required; global_absence_claimed is false, and gaps never silently suppress results.

## Action Safety And Rights/Risk

Allowed actions are metadata inspection, source/evidence viewing, comparison, and citation. Downloads, installs, execution, uploads, mirrors, and arbitrary URL fetches are disabled. P84 claims no rights clearance and no malware safety.

## Tie Break Policy

Tie breaks use preserve_current_order_v0 in examples. Random tie breaks are forbidden. Future tie breaks must be deterministic and evidence-explainable.

## No Hidden Suppression

No result may be suppressed without user-visible explanation. P84 performs no suppression at all. It defines a future explanation model with public user text, factor explanations, conflict explanations, gap explanations, and tie-break explanations.

## Public Projection

Future result cards, result merge groups, object pages, source pages, and comparison pages may show categorical explanations and expandable details. P84 publishes no numeric production score in v0 and changes no route behavior.

## Boundaries

P84 relates to result merge/deduplication, cross-source identity resolution, object/source/comparison pages, public search result cards, public index, source cache/evidence ledger, candidate index, and future compatibility-aware ranking. All integrations remain future/deferred. No runtime ranking, ranking store, DB table, connector execution, source sync execution, public index mutation, cache/ledger mutation, candidate promotion, telemetry, popularity ranking, ad ranking, user profiling, model calls, downloads, installs, or execution are added. These are no mutation guarantees.
