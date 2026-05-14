# Search Hunt Session Record

`SearchHuntSession` is the durable record for a local Search Hunt Session.

Required fields:

- `id`
- `query`
- `normalized_query`
- `state`
- `intent`
- `destination`
- `created_at`
- `updated_at`
- `index_snapshot_id`
- `reviewed_result_count`
- `candidate_result_count`
- `absence_report_id`
- `checked_layers`
- `unchecked_layers`
- `limitations`
- `warnings`
- `idempotency_key`
- `parent_id`

Checked layers in HUNT-01 are `reviewed_public_index`, `local_candidate_summary`, and `local_absence_report`.

Unchecked or deferred layers are `source_probes`, `WorkUnits`, `extraction`, `broader_connectors`, `synthetic_query_foundry`, and `AI_research_escalation`.

The record is not evidence and is not accepted truth. It is a resumable local investigation object.
