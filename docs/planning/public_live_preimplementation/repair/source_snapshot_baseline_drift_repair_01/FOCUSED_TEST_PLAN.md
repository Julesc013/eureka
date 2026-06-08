# Focused Test Plan

| Command | Purpose | Expected |
|---|---|---|
| `python scripts/validate_source_observation_seam.py --json` | Prove R0 source-observation seam baseline is green. | `status: pass`, zero forbidden vocabulary, zero network dependencies. |
| `python -m unittest tests.operations.test_local_worker_scripts.LocalWorkerScriptTests.test_validator_passes tests.runtime.test_source_observation_validation.SourceObservationValidationTests.test_validator_passes_or_warns_for_current_repo tests.runtime.test_ia_live_transport` | Prove both targeted labels and IA transport regression coverage. | Pass. |
| `python tools/validators/validate_ia_live_metadata_probe.py` | Prove the IA-specific bounded live metadata lane remains valid. | `status: pass`. |
| `python tools/validators/validate_ia_tls_trust.py` | Prove TLS verification posture remains valid. | `status: pass`. |
| `python scripts/check_architecture_boundaries.py` | Prove dependency boundaries are still valid. | Pass. |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | Confirm generated-artifact hygiene signal without repairing that family. | Pass or documented residual outside scope. |
| `py -3 .aide/scripts/aide_lite.py doctor` | AIDE operating health. | Pass. |
| `py -3 .aide/scripts/aide_lite.py validate` | AIDE validation. | Pass. |

Full unittest discovery remains an external gate and must not be run inside the
AI session.

