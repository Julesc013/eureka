# Validation

- `git diff --check`: PASS
- `python -m json.tool` for H2 live-probe contracts, policies, and report: PASS
- `python scripts/validate_h2_package_live_probe.py`: PASS
- `python scripts/run_h2_package_live_probe.py --source-id crates_io --request-key example_package_metadata --check`: PASS, blocked offline, no network
- `python scripts/summarize_h2_package_live_probe_outputs.py --input examples/connectors/h2_package_registries/live_probe_results --check`: PASS
- `python -m unittest tests.connectors.test_h2_package_live_probe`: PASS, 19 tests
- `python -m unittest tests.operations.test_h2_package_live_probe_scripts`: PASS, 9 tests
- `python -m unittest discover -s tests -t .`: PASS, 2948 tests
- `python scripts/check_architecture_boundaries.py`: PASS
- Existing H2/H1/H0/core validator sweep: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, diff-scope warnings only, 0 errors
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 14/14 golden tasks
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS

No live source call, package download, package-manager invocation, install/execute, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, or truth acceptance occurred.
