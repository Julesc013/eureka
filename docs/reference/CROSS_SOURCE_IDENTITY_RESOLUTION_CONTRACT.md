# Cross-Source Identity Resolution Contract v0

Cross-Source Identity Resolution Contract v0 is a contract-only, evidence-first governance layer for deciding whether records from different sources may refer to the same object, related objects, variants, versions, representations, source packages, releases, captures, or container members.

Identity resolution is not runtime yet. Identity resolution is not destructive deduplication, not merge runtime, not ranking runtime, not candidate promotion, not public query fanout, not source trust authority, not rights clearance, and not malware safety.

Boundary rules:

- No runtime identity resolution.
- No persistent identity store or runtime identity cluster store.
- No destructive merge and no records merged.
- No candidate promotion.
- No master index mutation, public index mutation, local index mutation, source cache mutation, evidence ledger mutation, or candidate index mutation.
- No live source call, connector execution, source sync execution, external API call, telemetry, download, install, execution, upload, account, or arbitrary URL fetch.
- No identity certainty without evidence and no source trust, rights clearance, or malware safety claim.

## Identity Relation Taxonomy

Relations include `exact_same_object`, `likely_same_object`, `possible_same_object`, `variant_of`, `version_of`, `release_of`, `representation_of`, `member_of`, `source_record_for`, `package_record_for`, `repository_record_for`, `capture_of`, `alias_of`, `near_match`, `different_object`, `conflicting_identity`, and `unknown`.

`relation_claim_not_truth` must be true and `global_merge_allowed` must be false. Exact same object requires strong identifier evidence or explicit future review.

## Identifier, Hash, And Intrinsic-ID Model

Identifier evidence records SHA-256, SHA-1, MD5, checksum, DOI, ISBN, package URL, SWHID, GitHub owner/repo, package name, version string, archive item identifier, Wayback URI-R, file name, member path, source native ID, or unknown values.

Exact intrinsic identifiers are stronger than names. Hashes/checksums/intrinsic IDs are stronger than text similarity, but hash matches are scoped: a file hash match is not automatically the same software product identity. Weak hashes such as MD5/SHA-1 require collision caution.

## Alias And Name Normalization

Name evidence may use case folding, punctuation folding, whitespace folding, version stripping, platform stripping, vendor alias, known alias, or unknown normalization. `name_match_not_sufficient_alone` must be true. Names and aliases alone are weak evidence.

## Version Platform Architecture

Version, platform, and architecture matching can indicate same version, different version, ranges, newer/older, same/overlapping/different platforms, same/overlapping/different architectures, unknown, or conflict. Version/platform evidence informs relation scope but does not create identity truth.

## Source And Provenance Evidence

Source/provenance evidence records whether sources provide the same source record, different sources with the same identifier, conflicting sources, source-only match, missing source, or unknown. `source_trust_claimed` is false and `provenance_not_truth` is true.

## Package Repository Archive Capture Identity

Package identity covers PyPI/npm package names, versions, and package URLs. Repository identity covers GitHub, Software Heritage, SourceForge, and unknown repository families. Archive identity covers Internet Archive, local fixture, recorded fixture, and unknown archive identifiers. Capture identity covers Wayback/CDX/Memento URI-R and timestamps with URI privacy review.

## Representation And Member Identity

Representation/member evidence can describe same, different, variant, parent-child, member-of-same-container, unknown, or conflicting relations. `payload_included` and `downloads_enabled` must be false. Member paths must be public-safe.

## Conflict Preservation, Confidence, And Review

Conflicts are preserved. `disagreement_preserved` must be true and `destructive_merge_allowed` must be false. Confidence classes are low, medium, high, or unknown, but `confidence_not_truth` must be true and `confidence_sufficient_for_merge_now` must be false.

Review requires human/policy/conflict/duplicate/promotion review as appropriate. `promotion_policy_required` and `destructive_merge_forbidden` must be true.

## Promotion And Merge Boundary

The promotion and merge boundary keeps `merge_runtime_implemented`, `merge_allowed_now`, `destructive_merge_allowed`, `canonicalization_allowed_now`, and `public_index_update_allowed_now` false. Future destinations are candidate index, master index review queue, and public index only after review.

## Public Projection And Privacy

Public projection can provide caveated relation labels to future public search result cards, object pages, source pages, and comparison pages. It does not mutate public search or the public index.

Public examples contain no private absolute paths, private URLs, private repositories, private packages, raw private queries, account/user identifiers, IP addresses, credentials, secrets, API keys, executable payloads, raw payload dumps, or real binaries.

## Relationships And Deferred Work

Identity resolution relates to object pages, source pages, comparison pages, public search, public index, source cache, evidence ledger, candidate index, candidate promotion policy, known absence pages, result merge/deduplication, evidence-weighted ranking, and compatibility-aware ranking.

Runtime identity resolution, persistent identity stores, canonicalization, destructive deduplication, record merging, candidate promotion, master-index updates, public-search identity badges, and hosted routes remain future work.
