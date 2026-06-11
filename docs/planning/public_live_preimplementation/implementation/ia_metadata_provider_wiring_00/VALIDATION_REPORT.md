# Validation Report

## Focused Tests

```text
python -m unittest tests.runtime.test_ia_metadata_provider_fallback
python -m unittest tests.runtime.test_surface_ia_metadata_fallback
python -m unittest tests.evals.test_ia_metadata_fallback_smoke
```

Result: `PASS`

## Standard Validation

Planned:

```text
git status --short
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 scripts/eureka_test_select.py --changed --failed-first --json
```

Result: `PASS`

Selector-recommended commands:

```text
python scripts/validate_test_lane_policy.py
python -m unittest tests.operations.test_test_lane_policy
python -m unittest tests.scripts.test_eureka_test_select
python -m unittest tests.scripts.test_validate_test_lane_policy
```

Result: `PASS`

Full unittest discovery is not run inside the AI session.
