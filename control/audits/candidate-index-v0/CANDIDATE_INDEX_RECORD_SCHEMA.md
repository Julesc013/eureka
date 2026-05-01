# Candidate Index Record Schema

`contracts/query/candidate_index_record.v0.json` requires:

- `schema_version`
- `candidate_id`
- `candidate_kind`
- `status`
- `created_by_tool`
- `candidate_identity`
- `candidate_type`
- `candidate_subject`
- `candidate_claims`
- `provenance`
- `input_refs`
- `evidence_refs`
- `source_policy`
- `confidence`
- `review`
- `conflicts`
- `visibility`
- `privacy`
- `rights_and_risk`
- `retention_policy`
- `limitations`
- `no_truth_guarantees`
- `no_mutation_guarantees`
- `notes`

The schema is contract-only and carries explicit false flags for runtime
candidate storage, promotion runtime, public search candidate injection,
telemetry, source-cache runtime, evidence-ledger runtime, master-index mutation,
external calls, and live probes.
