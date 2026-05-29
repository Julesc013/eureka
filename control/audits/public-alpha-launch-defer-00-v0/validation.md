# Validation

Required checks:

- `python scripts/validate_public_alpha_launch_defer.py`
- `python scripts/validate_public_alpha_launch_candidate.py`
- `python scripts/validate_public_alpha_deploy_dry_run.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `git diff --check`

Required non-claims:

- deployment_performed: false
- public_launch_performed: false
- production_readiness_claimed: false
- public_launch_readiness_claimed: false
- downloads_enabled: false
- extraction_enabled: false
- model_provider_enabled: false
