# Failure Labels Repaired

| Label | Repair | Focused result |
|---|---|---|
| `tests.operations.test_local_worker_scripts.LocalWorkerScriptTests.test_validator_passes` | No code change in this task; current tree already passes after prior queue/handoff repair. | Pass in focused unittest run. |
| `tests.runtime.test_source_observation_validation.SourceObservationValidationTests.test_validator_passes_or_warns_for_current_repo` | Removed the alternate Windows shell fallback from the IA live transport so the source-observation seam has no `subprocess` import or reserved vocabulary hit. | Pass in focused unittest run. |

The family should be considered locally repaired. It still requires a future
external full-discovery rerun for promotion-grade proof.

