# Baseline Expectation Map

| Expectation | Current status | Evidence |
|---|---|---|
| Source-observation seam has no forbidden task/control vocabulary | Repaired | Source-observation validator reports `forbidden_vocabulary_found: 0`. |
| Source-observation seam has no H-series dependency | Repaired | Source-observation validator reports `h_series_dependencies: 0`. |
| Source-observation seam has no banned shell/network dependency | Repaired | Source-observation validator reports `network_dependencies: 0`. |
| IA live metadata lane remains bounded and policy checked | Preserved | `tools/validators/validate_ia_live_metadata_probe.py` reports `status: pass`. |
| TLS verification posture remains secure | Preserved | `tools/validators/validate_ia_tls_trust.py` reports `status: pass`. |
| Local worker validator status is current | Repaired before this task, verified here | Focused unittest label passes. |
| Snapshot relay artifacts are not mutated | Unchanged | No snapshot paths modified. |
| Generated artifact drift is resolved | Not in scope | Deferred to `GENERATED-ARTIFACT-DRIFT-REPAIR-01`. |
| Contract/schema drift is resolved | Not in scope | Deferred to `CONTRACT-SCHEMA-DRIFT-REPAIR-01`. |

