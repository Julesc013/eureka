# Batch 0 Execution Packet

Batch 0 currently contains 39 pending manual observation slots across 13 queries and 3 manually searched external systems.

Canonical guidance:

- `docs/operations/MANUAL_OBSERVATION_BATCH_0_EXECUTION.md`
- `docs/operations/MANUAL_OBSERVATION_SLOT_COMPLETION_GUIDE.md`
- `docs/operations/MANUAL_OBSERVATION_PROTOCOL.md`
- `docs/operations/MANUAL_OBSERVATION_ANTI_FABRICATION_CHECKLIST.md`
- `docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md`

Local inputs:

- `batch_manifest.json`
- `observations/pending_batch_0_observations.json`
- `observation_template.batch_0.json`

Run:

```powershell
python scripts/prepare_manual_observation_batch0_execution.py --check
python scripts/validate_manual_observation_batch0_execution.py
```

This packet does not record actual observations. Every slot remains pending until a human performs the observation and records the required fields.
