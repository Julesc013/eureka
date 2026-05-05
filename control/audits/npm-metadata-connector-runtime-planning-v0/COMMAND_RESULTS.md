# Command Results

Initial local inspection completed. P75 approval artifacts are present, but `connector_approved_now` is false. Package identity, scoped-package, dependency metadata, lifecycle-script, token/auth, source policy, package download/install/dependency/script boundaries, and operator values remain pending.

P91 validation passed:

- `python scripts/validate_npm_metadata_connector_runtime_plan.py`
- `python scripts/validate_npm_metadata_connector_runtime_plan.py --json`
- `python -m unittest tests.operations.test_npm_metadata_connector_runtime_plan tests.scripts.test_validate_npm_metadata_connector_runtime_plan`

Required related validators and local lanes passed, including npm approval validation, P87-P90 runtime plans, source sync, source cache/evidence ledger, P79-P86 contract/planning validators, public search safety/static checks, archive resolution evals, search usefulness audit, full Python unit discovery, architecture boundaries, and `git diff --check`.

Hosted deployment remains gated: backend URL is not configured, static route verification remains failed, and Manual Observation Batch 0 remains 0 observed / 39 pending.

Optional `gh` and `cargo` targets were unavailable in this environment.
