# Validation Results

Command:

```bash
python scripts/validate_pack_set.py --all-examples --json
```

Current summary:

- total: 5
- passed: 5
- failed: 0
- unavailable: 0
- unknown_type: 0

Per-example status:

- `source_pack`: `examples/source_packs/minimal_recorded_source_pack_v0` passed
- `evidence_pack`: `examples/evidence_packs/minimal_evidence_pack_v0` passed
- `index_pack`: `examples/index_packs/minimal_index_pack_v0` passed
- `contribution_pack`: `examples/contribution_packs/minimal_contribution_pack_v0` passed
- `master_index_review_queue`: `examples/master_index_review_queue/minimal_review_queue_v0` passed

The aggregate report records `mutation_performed=false`,
`import_performed=false`, `staging_performed=false`,
`indexing_performed=false`, and `network_performed=false`.

