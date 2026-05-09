# Validation

- `git diff --check`: PASS
- `python -m json.tool` on H0 connector contracts, inventories, and report: PASS, 17 files
- `python scripts/validate_connector_interface_foundation.py`: PASS
- `python scripts/summarize_connector_families.py --input examples/connectors/core/families --check`: PASS
- `python scripts/run_connector_fixture_replay.py --request examples/connectors/core/fixture_replay/minimal_fixture_replay_request_v0.json --check`: PASS
- `python scripts/evaluate_connector_policy.py --request examples/connectors/core/live_probe/policy_blocked_live_probe_request_v0.json --check`: PASS
- `python -m unittest tests.connectors.test_connector_interface_foundation`: PASS, 13 tests
- `python -m unittest tests.operations.test_connector_interface_foundation_scripts`: PASS, 10 tests
- `python -m unittest discover -s tests -t .`: PASS, 2632 tests
- `python scripts/check_architecture_boundaries.py`: PASS, 505 Python files
- Existing H0/IA/local-foundry validators: PASS
- AIDE Lite doctor/validate/test/selftest/eval/review-pack/adapter validate: PASS
- AIDE Lite verify: WARN with zero errors; remaining warnings were optional latest-review-packet references.
