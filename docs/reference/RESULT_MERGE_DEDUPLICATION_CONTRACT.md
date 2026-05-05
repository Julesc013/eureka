# Result Merge and Deduplication Contract v0

Result Merge and Deduplication Contract v0 is a contract-only, evidence-first governance layer for future grouping of duplicate, near-duplicate, variant, source-duplicate, parent/child, member, mirror, conflicting, not-duplicate, and unknown search results.

Result merge is not identity truth. Result merge is not destructive record merge. Result merge is not ranking, not candidate promotion, not source trust, not evidence acceptance, not rights clearance, and not malware safety.

Boundary rules:

- No runtime result grouping or runtime deduplication.
- No persistent merge group store.
- No public search result ordering, ranking, hiding, suppression, or collapse change.
- No records merged, duplicates deleted, destructive merge, candidate promotion, master index mutation, public index mutation, local index mutation, source cache mutation, evidence ledger mutation, or candidate index mutation.
- No live source call, connector execution, source sync execution, external API call, telemetry, download, install, execution, upload, account, or arbitrary URL fetch.

## Merge Relation Taxonomy

Relations include `exact_duplicate_result`, `near_duplicate_result`, `variant_result`, `same_object_different_source`, `same_object_different_representation`, `same_version_different_representation`, `same_source_duplicate`, `parent_child_result`, `member_of_result`, `source_mirror_result`, `conflicting_duplicate_claim`, `not_duplicate`, and `unknown`.

Every relation requires `relation_claim_not_truth: true` and `destructive_merge_allowed: false`. Exact duplicate examples require strong grouping evidence or review.

## Duplicate Near-Duplicate Variant Conflict

Exact duplicates require strong intrinsic identifiers, checksums, package URLs, source native IDs, SWHIDs, archive identifiers, or reviewed identity references. Near duplicates use weaker evidence such as normalized names or aliases and require review. Variants preserve distinct representations or versions. Conflict groups preserve disagreement and must remain expandable.

## Grouping Criteria Strength

Strong criteria include exact identifiers, checksum matches, source native IDs, package URLs, SWHIDs, archive identifiers, and reviewed identity references. Medium criteria include scoped object/version/representation/member refs. Weak criteria include normalized title, alias, source family, or text similarity. Weak name match is not sufficient for exact duplicate grouping.

## Canonical Display And Transparency

Canonical display record is not truth. It is a UI convenience only. Alternative results must be preserved. Collapsed results must be transparent and expandable. Conflicts must not be hidden. No result may be suppressed without user-visible explanation.

## Preservation And Relationships

Source, evidence, and provenance refs must be preserved. Source trust is not claimed. Cross-source identity resolution may inform grouping but does not authorize destructive merge. Object pages, source pages, and comparison pages can use future relation labels only after governed integration. Public search result cards and APIs may project merge groups later, but P83 does not mutate public search or public index behavior.

## Deferred Work

Runtime grouping, runtime deduplication, ranking integration, persistent merge stores, public-search expand/collapse UI, evidence-weighted ranking, compatibility-aware ranking, and hosted runtime integration remain future work. These are future ranking contracts and runtime-planning items, not P83 behavior.

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
