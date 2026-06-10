# Failure Family Inventory

Rerun 05 completed full discovery and produced 39 failures, 0 errors, and 24
raw unittest failure-family hashes.

The failures are classified as current-state validator drift, not as an import
or discovery failure.

| Classified Family | Failures | Raw Families | Representative Signals | Recommended Next Task |
|---|---:|---:|---|---|
| `historical_queue_validator_drift` | 17 | 12 | HUNT and adjacent agent/replay validators expect old HUNT queue successors while current queue waits for external artifact evidence | `HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-05` |
| `historical_local_queue_validator_drift` | 16 | 9 | LOCAL validators expect old LOCAL queue successors while current queue waits for external artifact evidence | `HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-05` |
| `historical_dev_to_main_promotion_validator_drift` | 4 | 1 | old promotion validators expect `origin/main` and `origin/dev` parity that is not true for current `dev` | `HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-05` |
| `public_alpha_defer_queue_validator_drift` | 2 | 1 | launch-defer validators expect an older active-discovery queue posture | `HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-05` |

## Clear Families

| Family | Count | Status |
|---|---:|---|
| `import_or_discovery_error` | 0 | clear |
| `architecture_boundary_drift` | 0 | clear from compact summary; separate boundary check still required |
| `source_snapshot_baseline_drift` | 0 | not identified |
| `generated_artifact_drift` | 0 | not identified |
| `contract_schema_drift` | 0 | not identified |
| `artifact_corpus_gate_drift` | 0 | not identified |
| `reviewed_artifact_gate_drift` | 0 | not identified |
| `runtime_surface_phase_drift` | 0 | not identified |
| `tsis_phase_boundary_drift` | 0 | not identified |
| `public_index_generated_drift` | 0 | not identified |
| `checksum_manifest_drift` | 0 | not identified |
| `legacy_leakage_validator_drift` | 0 | not identified |
| `test_fixture_drift` | 0 | not identified |
| `external_summary_reference_drift` | 0 | not identified |
| `validator_expectation_drift` | 39 | represented as historical queue validator drift |
| `unknown` | 0 | no unknown family selected |

## Repair Boundary

This ingest does not repair the failures. The next task should update or
quarantine historical queue/promotion validators so full discovery can evaluate
current repo posture without expecting obsolete queue successors.

