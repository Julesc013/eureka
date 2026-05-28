# Validation Matrix

Fresh external full discovery:

- status: pass
- tests_run: 5057
- failures: 0
- errors: 0
- exit_code: 0
- head: `317092ac431d1bf2882b199f90e66d78c097e99b`

Focused validation lane:

- `python scripts/validate_dev_to_main_promotion_04.py`
- `python scripts/validate_public_alpha_readonly_closeout.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_public_alpha_hosting_readiness.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/validate_source_wave.py`
- `python scripts/validate_source_action_kernel.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_dev_to_main_promotion_04`
- `python -m unittest tests.scripts.test_validate_dev_to_main_promotion_04`

Full discovery was not run inside AI.
