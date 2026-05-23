# EvidencePage View Model Contract

EvidencePageView v0 defines the public meaning layer for evidence records,
evidence candidates, observations, claims, snippets, source locators,
provenance, confidence, review posture, conflicts, and limitations. It is
contract and governance work only.

## Purpose

Evidence is not truth by default. EvidencePageView makes evidence identity,
claim and observation posture, source locator context, snippet posture,
provenance, related source/object/candidate/pack/review refs, confidence,
conflicts, review requirements, rights/risk/privacy posture, allowed actions,
blocked actions, limitations, and warnings visible to every renderer.

## Required Meaning

EvidencePageView preserves:

- canonical evidence identity and route
- evidence type and status
- claim type, observation type, source locator, snippet, and provenance posture
- related source, object, candidate, pack, and review refs
- confidence, uncertainty, conflict, and review state
- accepted public status and master-index mutation boundary
- rights, risk, and privacy posture
- allowed actions and blocked actions
- limitations, warnings, and unresolved gaps

## Truth Boundaries

EvidencePageView explicitly forbids converting:

- source observations into accepted truth
- evidence candidates into verified facts
- contribution claims into accepted public records
- AI drafts into evidence truth
- discussion comments into compatibility truth
- manual observation placeholders into completed external baselines
- checksum claims into authenticity proof without evidence
- metadata claims into rights clearance
- evidence pages into master-index mutation

## Current Boundary

Current examples must keep review required, accepted public status false, and
master-index mutation false. They must not claim hosted backend, live probes,
source sync, downloads, uploads, accounts, telemetry, rights clearance, malware
safety, verified installability, safe execution, authorized bulk access, or
production suitability.

## Related Contracts

- `contracts/view/pages/evidence_page.v0.json`
- `control/inventory/publication/evidence_page_view_model_policy.json`
- `docs/reference/EVIDENCE_PACK_CONTRACT.md`
- `docs/reference/SOURCE_PACK_CONTRACT.md`
- `docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No evidence ledger mutation.
- No source cache, source connector, live probe, or source sync runtime.
- No accepted public truth or master-index mutation from evidence pages.
