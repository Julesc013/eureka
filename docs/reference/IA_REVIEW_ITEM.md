# IA Review Item

An IA review item is a local queue record derived from a provisional IA
candidate-index record.

Required fields include:

- `review_item_id`
- `source_id`
- `candidate_id`
- `candidate_kind`
- `evidence_ids`
- `source_cache_record_ids`
- `observation_ids`
- `title`
- `summary`
- `source_locator`
- `provenance`
- `uncertainty`
- `limitations`
- `risk_flags`
- `rights_flags`
- `suggested_decision`
- `review_required`
- `accepted_truth`

Required invariants:

- `review_required` is true
- `accepted_truth` is false
- reviewed and master index mutation flags are false
- `raw_response_committed` is false
- `download_performed` is false

The durable review queue payload uses sanitized field names because the shared
review queue rejects reserved public-truth vocabulary.

