# TRACK-A-14 Projection Gap Report

## Current Aligned Artifacts

- Object-like demo pages exist for Firefox XP compatibility, a member file
  inside a support CD, and article scan fixture content.
- Source artifacts exist in standard HTML, lite HTML, text, and JSON summary
  forms.
- The file-tree seed surface records public data summary references without
  download or live-backend claims.
- `site/dist/demo/absence-example.html` records bounded absence and explicitly
  avoids global non-existence claims.
- `site/dist/demo/comparison-example.html` preserves disagreement instead of
  merging records or selecting truth.

## Missing Or Unknown Semantic Mappings

- Current artifacts are not generated from canonical `ObjectPageView`,
  `SourcePageView`, `NeedPageView`, or `CandidatePageView` fixtures.
- Future canonical object, need, and candidate page routes are not active.
- Current source-list artifacts are SourcePage-adjacent summaries, not
  SourcePageView detail projections.
- No audited artifact embeds a canonical `view_model_id` for these view
  families.

## Object Gaps

- Demo result pages preserve useful object semantics but remain illustrative
  static snapshots.
- Object identity, member lineage, source/evidence posture, rights/risk posture,
  and blocked actions are not uniformly machine-verifiable across all object
  artifacts.
- No canonical object page artifact exists under a future `/objects/{object_id}`
  route.

## Source Gaps

- Source summary pages preserve fixture and placeholder posture, but source
  policy, cache, and evidence-ledger semantics are partial in text/lite forms.
- File-tree source-adjacent artifacts are useful as public-data manifests, but
  they are not SourcePageView projections.
- Source detail pages are not currently projected as canonical `SourcePageView`
  pages.
- Recorded fixture sources are correctly not treated as live connectors.

## Need Gaps

- Need semantics are currently visible only through the absence demo.
- Demand, privacy/poisoning, source-not-checked, near-match, and work-unit
  posture are partial or not machine-verified.
- No canonical NeedPage route or projection exists.

## Candidate Gaps

- Candidate semantics are currently inferred from comparison/demo data.
- Review-required, accepted-public-status false, and master-index-mutation false
  posture are only partially visible and need canonical fixture projection.
- No canonical CandidatePage route or projection exists.

## Recommended Next Work

Continue with `TRACK-A-15 - Temporal Minimal Search design token contract`, then
renderer parity and Track A integration audit. Add a later follow-up for object,
source, need, and candidate projection fixtures and a dry-run plan before any
public route or renderer refactor.

## Risks

- This audit uses conservative substring and JSON-field checks, not full HTML
  renderer parity.
- WARN status is expected until canonical fixtures and projection generators
  exist for these view families.

## No-Goals Preserved

No static site artifacts were changed or regenerated. No hosted backend, live
source behavior, downloads, uploads, accounts, telemetry, public truth
promotion, exhaustive search, or automatic merge/dedup/promotion was enabled or
claimed.
