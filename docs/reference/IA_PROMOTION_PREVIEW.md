# IA Promotion Preview

An IA promotion preview is a proposed reviewed-record shape built from an
approved IA review decision.

Required fields include:

- `promotion_preview_id`
- `review_decision_id`
- `candidate_id`
- `proposed_reviewed_record_id`
- `proposed_title`
- `proposed_summary`
- `source_locator`
- `evidence_ids`
- `source_cache_record_ids`
- `provenance`
- `uncertainty`
- `limitations`
- `rights_flags`
- `risk_flags`
- `preview_only`
- `accepted_truth`

Required invariants:

- `preview_only` is true
- `review_required` is true
- `accepted_truth` is false
- `reviewed_index_write_performed` is false
- `master_index_write_performed` is false
- `raw_response_committed` is false
- `download_performed` is false

IA-06 promotion previews are handoff material for IA-07. They are not reviewed
records and do not mutate reviewed or master indexes.
