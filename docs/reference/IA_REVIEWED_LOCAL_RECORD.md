# IA Reviewed Local Record

An IA reviewed local record is a local projection created from an explicit IA
review decision and promotion preview. It is scoped to a local/temp instance and
does not represent master truth or public hosted search.

Required fields include:

- `reviewed_record_id`
- `source_id`
- `source_family`
- `source_locator`
- `promotion_preview_id`
- `review_decision_id`
- `candidate_id`
- `evidence_ids`
- `source_cache_record_ids`
- `observation_ids`
- `title`
- `summary`
- `provenance`
- `uncertainty`
- `limitations`
- `rights_flags`
- `risk_flags`
- `review_status`

Required invariants:

- `reviewed_local_index_record: true`
- `master_index_record: false`
- `public_hosted_record: false`
- `raw_response_committed: false`
- `download_performed: false`

The record must preserve IA source provenance, evidence IDs, uncertainty,
limitations, rights flags, risk flags, and source locator details.
