# G0 Foundation Runbook

Use G0 with deterministic fixture data:

1. Score: `python scripts/eureka_g0_score.py --fixture examples/search_quality/sample_quality_fixture.json --json`
2. Explain: `python scripts/eureka_g0_explain.py --fixture examples/search_quality/sample_quality_fixture.json --json`
3. Identity: `python scripts/eureka_g0_identity.py --fixture examples/search_quality/sample_quality_fixture.json --json`
4. User cost: `python scripts/eureka_g0_user_cost.py --fixture examples/search_quality/sample_quality_fixture.json --json`
5. Console: `python scripts/eureka_g0_smoke.py --fixture examples/search_quality/sample_quality_fixture.json --projection operator_workbench --json`

Validation:

- `python scripts/validate_g0_foundation.py`
- focused G0 runtime and script tests
- selected test lane router checks

Keep the boundary read-only: no source probes, no downloads, no extraction, no
provider calls, no index mutation, and no production or public launch claims.
