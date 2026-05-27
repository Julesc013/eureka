# Validation

- `python scripts/validate_public_alpha_readonly.py --json`: PASS
- `python -m unittest runtime.gateway.tests.test_public_alpha_readonly surfaces.web.tests.test_public_alpha_readonly_routes tests.scripts.test_validate_public_alpha_readonly`: PASS
- `python -m unittest surfaces.web.tests.test_public_search_routes surfaces.web.tests.test_public_alpha_web surfaces.web.tests.test_public_alpha_http_api`: PASS
- `python -m unittest tests.runtime.test_relay_projection tests.runtime.test_snapshot_records tests.operations.test_snapshot_relay_smoke`: PASS
- `python scripts/validate_public_search_contract.py --json`: PASS
- `python scripts/validate_public_search_index.py --json`: PASS
- `python scripts/validate_snapshot_relay.py`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `python .aide/scripts/aide_lite.py doctor`: PASS
- `python .aide/scripts/aide_lite.py validate`: PASS
- `python .aide/scripts/aide_lite.py test`: PASS
- `python .aide/scripts/aide_lite.py selftest`: PASS
- `python .aide/scripts/aide_lite.py verify`: PASS
- `python .aide/scripts/aide_lite.py review-pack`: PASS
- `git diff --check`: PASS

Full unittest discovery was not run inside this AI session.
