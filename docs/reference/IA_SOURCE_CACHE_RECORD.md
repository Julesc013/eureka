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

## IA-04 Handoff

IA-04 consumes these source-cache records to build evidence-ledger candidates.
The source-cache record remains an observation, and the evidence record remains
a claim candidate. This handoff does not accept evidence, rebuild an index, or
promote IA metadata to reviewed local truth.

## IA-05 Handoff

IA-05 consumes IA evidence candidates derived from source-cache records to build
provisional candidate-index records. The source-cache record remains an
observation and the candidate record remains unreviewed.

## IA-06 Handoff

IA-06 keeps source-cache provenance traceable in review queue items and
promotion previews. It does not modify source-cache records or promote them to
truth.
