# ReviewPage View Model Contract

ReviewPageView v0 defines the public meaning layer for review queue entries,
validation posture, review decisions, deferrals, rejections, conflicts, policy
checks, and promotion requirements. It is contract and governance work only.
It does not implement hosted moderation, accounts, write routes, public
submission runtime, review runtime, or master-index mutation.

## Purpose

A review record is governance evidence, not automatic promotion. ReviewPageView
makes review identity, status, decision posture, subject refs, candidate refs,
pack refs, evidence refs, source refs, validation posture, acceptance
requirements, rejection and deferral state, conflicts, rights/risk/privacy,
provenance, master-index boundary, actions, blocked actions, limitations, and
warnings visible to every renderer.

## Required Meaning

ReviewPageView preserves:

- canonical review identity and route
- review type, status, and decision posture
- queue entry status and subject links
- validation status
- acceptance requirements, rejection reason, deferral reason, and conflicts
- rights, risk, and privacy posture
- provenance and lineage
- master-index mutation boundary
- accepted public status and promotion requirements
- allowed actions and blocked actions
- limitations, warnings, and unresolved gaps

## Current Boundary

Current examples must keep these false or unavailable:

- hosted moderation
- account-backed review
- write routes
- public submission runtime
- review runtime
- accepted public status
- public truth claims
- master-index mutation
- hosted backend, live probes, source sync, downloads, uploads, accounts,
  telemetry, rights clearance, malware safety, verified installability, safe
  execution, authorized bulk access, or production suitability

## Truth Boundaries

ReviewPageView explicitly forbids converting:

- demand signals into object truth
- source observations into accepted truth
- evidence candidates into verified facts
- contribution items into accepted public records
- AI drafts into evidence truth
- review queue entries into master-index mutation without a separate accepted
  review workflow

## Related Contracts

- `contracts/view/pages/review_page.v0.json`
- `control/inventory/publication/review_page_view_model_policy.json`
- `contracts/schema/control/tasks/master_index/review_queue_entry.v0.json`
- `contracts/schema/control/tasks/master_index/review_queue_manifest.v0.json`
- `contracts/index/master/review_decision.v0.json`
- `docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`
- `docs/reference/CANDIDATE_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/PACK_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No hosted moderation, account-backed review, write routes, public submission
  runtime, or review runtime.
- No master-index mutation.
- No public truth from review records, candidates, packs, source observations,
  evidence candidates, contribution items, or AI drafts.
