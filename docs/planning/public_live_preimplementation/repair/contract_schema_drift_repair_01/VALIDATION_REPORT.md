# Validation Report

## Targeted Labels

| Item | Result |
|---|---|
| Targeted family | `contract_schema_drift` |
| Targeted test module | `tests.scripts.test_validate_temporal_semantic_interface_system` |
| Targeted labels repaired | `test_validator_passes`, `test_cli_json_passes` |
| Targeted labels residual | none in focused validation |

## Focused Validation Already Run

| Command | Result |
|---|---|
| `python -m unittest tests.scripts.test_validate_temporal_semantic_interface_system` | PASS; 7 tests. |
| `python scripts/validate_temporal_semantic_interface_system.py --json` | PASS; `status: pass`, `errors: []`. |

## Final Required Validation

| Command | Result |
|---|---|
| `git diff --check` | PASS; line-ending warnings only for touched files. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS. |
| `python scripts/check_architecture_boundaries.py` | PASS; 921 Python files checked, no violations. |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS; no generated drift paths, forbidden generated outputs, or site/public-index drift. |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS; selected L0 static preflight plus L1/L2 validator/test lanes; full discovery deferred. |
| `python -m unittest tests.scripts.test_validate_test_lane_policy tests.operations.test_test_lane_policy tests.scripts.test_eureka_test_select` | PASS; 6 tests. |
| `python scripts/validate_test_lane_policy.py` | PASS; status valid. |
| `python -m unittest tests.contracts.test_temporal_semantic_interface_contracts` | PASS; 2 tests. |

## Boundaries

| Boundary | Result |
|---|---|
| full discovery run inside AI | no |
| external full-discovery rerun needed | yes |
| public alpha gate | blocked |
| `dev -> main` gate | blocked |
| source/snapshot release gate | blocked |
| protected paths changed | none expected |
| queue mutation | `.aide/queue/index.yaml` only |
| canon mutation | none |
| runtime behavior mutation | none |
