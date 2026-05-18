# IA Source Cache Record

IA source-cache records preserve Internet Archive metadata observations with
provenance and review boundaries.

Required fields include:

- `record_id`
- `source_id`
- `source_kind`
- `observation_id`
- `observation_kind`
- `source_locator`
- `observed_at`
- `captured_at`
- `request_policy_id`
- `endpoint_class`
- `normalized_summary`
- `response_summary_hash`
- `ttl`
- `expires_at`

Required invariants:

- `review_required` is true
- `accepted_truth` is false
- `raw_response_committed` is false
- `evidence_ledger_write_performed` is false
- `index_mutation_performed` is false
- `download_performed` is false

The generic durable cache entry stores a sanitized payload so reserved public
truth vocabulary is not embedded in the shared source-cache payload.
