# ComparePage View Model Contract

ComparePageView v0 defines the public meaning layer for comparing objects,
versions, states, sources, representations, packs, candidates, evidence
records, compatibility claims, and near matches. It is contract and governance
work only.

## Purpose

Comparison preserves disagreement. ComparePageView makes comparison identity,
subject refs, comparison type and status, axes, shared fields, differing
fields, conflicts, evidence posture, source posture, compatibility posture,
representation posture, rights/risk posture, review posture, deduplication
posture, identity resolution posture, allowed actions, blocked actions,
limitations, and warnings visible to every renderer.

## Required Meaning

ComparePageView preserves:

- canonical comparison identity and route
- compared subject refs and comparison axes
- shared fields, differing fields, disagreements, and conflicts
- missing evidence and uncertain identity
- source-specific differences
- candidate, review, deduplication, and identity-resolution posture
- rights, risk, compatibility, and representation posture
- allowed actions and blocked actions
- limitations, warnings, and unresolved gaps

## Truth Boundaries

ComparePageView must not automatically:

- merge records
- deduplicate records
- accept records
- reject records
- promote records
- mutate the master index
- hide disagreement or conflicting evidence

## Current Boundary

Current examples must keep automatic merge, automatic deduplication, automatic
promotion, accepted public status, and master-index mutation false. They must
not claim hosted backend, live probes, downloads, uploads, accounts, telemetry,
rights clearance, malware safety, verified installability, safe execution,
authorized bulk access, or production suitability.

## Related Contracts

- `contracts/view/pages/compare_page.v0.json`
- `control/inventory/publication/compare_page_view_model_policy.json`
- `docs/reference/OBJECT_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/CANDIDATE_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/EVIDENCE_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No automatic merge, deduplication, promotion, acceptance, rejection, or
  master-index mutation.
- No hidden conflict or disagreement suppression.
