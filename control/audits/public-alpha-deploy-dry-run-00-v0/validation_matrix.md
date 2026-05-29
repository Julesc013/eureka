# Validation Matrix

Focused validation only:

- `python scripts/validate_public_alpha_deploy_dry_run.py`
- `python scripts/validate_public_alpha_launch_candidate.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_public_alpha_hosting_readiness.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_public_alpha_deploy_dry_run`
- `python -m unittest tests.scripts.test_validate_public_alpha_deploy_dry_run`

Full unittest discovery is not run inside AI for this dry-run task.
