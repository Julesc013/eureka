# IA Evidence Record

IA evidence records are bounded claim candidates derived from IA metadata
source-cache records.

Required fields include:

- `evidence_id`
- `source_id`
- `source_cache_record_id`
- `observation_id`
- `claim_id`
- `claim_kind`
- `claim_value`
- `claim_value_normalized`
- `claim_subject`
- `claim_scope`
- `source_locator`
- `provenance`
- `support_level`
- `confidence`
- `uncertainty`
- `limitations`
- `review_required`
- `accepted_truth`
- `reviewer_decision`

Required invariants:

- `review_required` is true
- `accepted_truth` is false
- `reviewer_decision` is pending
- candidate, reviewed, and master index mutation flags are false
- `raw_response_committed` is false
- `download_performed` is false

The durable evidence-ledger payload uses sanitized field names so the shared
ledger does not store reserved public-truth vocabulary. IA audit reports keep
the explicit boundary booleans for operator review.
