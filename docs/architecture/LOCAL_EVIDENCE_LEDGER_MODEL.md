# Local Evidence Ledger Model

The local evidence ledger model is a future append-style evidence candidate and
provenance model. It sits after source cache planning and before candidate
promotion, evidence pack export, review queue integration, public index use, or
master-index review. In short: source cache comes before evidence ledger, and
evidence ledger comes before candidate promotion.

## Model Layers

`source cache observation`
: A future reviewed source-cache record or fixture output. It is not evidence
truth.

`evidence candidate`
: A claim or observation draft with provenance, review status, confidence or
uncertainty, limitations, and conflict notes.

`review status record`
: A future append-style event recording review state or decision. It cannot
create automatic public truth.

`provenance link`
: A relationship among source locator, source-cache record, evidence candidate,
and review status.

`reviewed evidence`
: Out of scope for B-14 and blocked until future evidence-ledger runtime and
review policy exist.

## Record Statuses And Types

Record statuses include planned, fixture-only, evidence candidate,
source-observation candidate, metadata claim candidate, identity claim
candidate, compatibility claim candidate, checksum claim candidate,
filename/member claim candidate, conflict, needs review, evidence needed,
blocked, stale, superseded, and deferred states.

Record types include source observation, source-cache-derived claim, metadata
claim, identity claim, compatibility claim, checksum claim, filename/member
claim, source locator, manual observation claim, pack claim, contribution
claim, conflict record, review status record, provenance link, AI draft future,
and discussion-derived future.

## Truth Boundary

Required current truth boundary:

- `evidence_record_is_public_truth: false`
- `evidence_record_is_accepted_evidence: false`
- `evidence_record_can_mutate_master_index: false`
- `evidence_record_can_claim_rights_clearance: false`
- `evidence_record_can_claim_malware_safety: false`
- `human_review_required_for_downstream_use: true`

## Source Cache Bridge

The bridge maps reviewed source-cache material into evidence candidates and
provenance links. It must preserve conflicts and limitations. It must not turn
source observations into accepted truth, evidence candidates into verified
facts, AI drafts into evidence truth, contribution claims into public records,
metadata claims into rights clearance, checksum claims into authenticity proof
without evidence, or compatibility claims into verified compatibility without
review.

## Rollout

The rollout phases are:

- `phase_0_planning_only`
- `phase_1_fixture_only_runtime_future`
- `phase_2_source_cache_bridge_fixture_future`
- `phase_3_evidence_candidate_runtime_future`
- `phase_4_review_queue_integration_future`
- `phase_5_evidence_pack_export_future`
- `phase_6_reviewed_public_index_bridge_future`

B-14 only authorizes phase 0. Later phases require separate reviewed tasks.
