# Probe Queue Item Schema

`contracts/query/probe_queue_item.v0.json` requires:

- `probe_item_id`, `probe_item_kind`, `status`, and `created_by_tool`
- `probe_identity`
- `probe_kind`
- `source_policy`
- `input_refs`
- `target`
- `priority`
- `scheduling`
- `expected_outputs`
- `safety_requirements`
- `privacy`, `retention_policy`, and `aggregation_policy`
- `no_execution_guarantees` and `no_mutation_guarantees`

The schema is contract-only and requires hard false guarantees for probe
execution, live source calls, external calls, source cache mutation, evidence
ledger mutation, candidate-index mutation, local-index mutation, and
master-index mutation.
