# Focused Tests

## Targeted Tests

| Command | Expected result | Purpose |
|---|---|---|
| `python -m unittest tests.scripts.test_validate_temporal_semantic_interface_system` | PASS | Reproduces and verifies the contract/schema drift repair. |
| `python scripts/validate_temporal_semantic_interface_system.py --json` | PASS | Verifies the CLI validator no longer fails current repo phase state. |

## Adjacent Tests And Validators

The final validation pass should also run:

- `git diff --check`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `py -3 scripts/eureka_test_select.py --changed --failed-first --json`

If the selector recommends extra focused tests, run them.

