# CandidatePage View Model Contract

`contracts/views/candidate_page.v0.json` defines the first canonical public
CandidatePage view model for Track A. A candidate is provisional review context,
not public truth. It may come from search needs, source observations, source
cache records, evidence packs, contribution packs, index packs, manual
observations, future extraction, future node work, discussion-to-evidence
workflows, or future AI drafts.

Inventory:

- `control/inventory/publication/candidate_page_view_model_policy.json`

Examples:

- `examples/view_models/candidate_page/minimal_candidate_page_v0.json`
- `examples/view_models/candidate_page/source_observed_candidate_page_v0.json`
- `examples/view_models/candidate_page/evidence_candidate_page_v0.json`
- `examples/view_models/candidate_page/policy_blocked_candidate_page_v0.json`

## Doctrine

A Eureka candidate is not truth. It is a provisional finding awaiting evidence,
review, rejection, deferral, deduplication, conflict preservation, or future
promotion. Renderers may simplify presentation, but must not change candidate
identity, origin, provisional status, evidence posture, source posture,
provenance, conflicts, review state, rights/risk posture, allowed actions,
blocked actions, limitations, or gaps.

## Relationship To Existing Contracts

CandidatePageView references these governance inputs:

- `control/schemas/previews/query/candidate_index_record.v0.json`
- `control/schemas/previews/query/candidate_lifecycle.v0.json`
- `control/schemas/previews/query/candidate_promotion_policy.v0.json`
- `docs/reference/CANDIDATE_INDEX_CONTRACT.md`
- `docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`
- `docs/reference/CONTRIBUTION_PACK_CONTRACT.md`
- `control/inventory/publication/route_view_representation_matrix.json`
- `control/inventory/publication/semantic_renderer_parity_policy.json`

This contract does not create candidate runtime storage, candidate promotion,
review runtime, public search injection, source cache writes, evidence ledger
writes, source sync, public routes, or master-index mutation.

## Required Meaning

Every CandidatePageView record carries:

- canonical candidate identity and route
- candidate status, type, origin, and source refs
- proposed object and state summaries
- evidence, source, and provenance posture
- compatibility, rights, and risk posture
- review requirements and acceptance limits
- conflict and deduplication summaries
- related need, object, source, pack, and future work-unit refs
- allowed and blocked actions
- limitations, warnings, representation hints, and semantic requirements

## Truth Boundaries

CandidatePageView explicitly forbids converting:

- AI draft into evidence truth
- source observation into accepted truth
- evidence candidate into verified fact
- contribution item into accepted public record
- discussion comment into compatibility truth
- demand signal into object truth

Current examples require `review_required: true`,
`master_index_mutation_allowed: false`, and `accepted_public_status: false`.

## Blocked Claims

Current examples must not claim rights clearance, malware safety, verified
installability, authorized download, safe execution, public acceptance,
production suitability, hosted backend behavior, live probes, source sync,
uploads, accounts, telemetry, or master-index mutation.

## Representation Hints

The first policy covers `standard_html`, `lite_html`, `html32`, `text`,
`file_tree`, `api_json`, `manifest_json`, `snapshot_future`, `relay_future`,
`terminal_future`, `native_card_future`, and `print`.

Hints are renderer guidance only. They must not alter candidate meaning or hide
review-required status, conflicts, evidence caveats, rights/risk uncertainty, or
blocked actions.

## Validation

Run:

- `python scripts/validate_need_candidate_page_view_models.py`
- `python -m unittest tests.contracts.test_need_candidate_page_view_models`
