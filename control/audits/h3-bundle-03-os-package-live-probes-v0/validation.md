# Validation

H3-BUNDLE-03 focused validation passed for the offline live-probe framework.

| Command | Result |
| --- | --- |
| `git diff --check` | PASS |
| `python scripts/validate_h3_os_package_live_probe.py` | PASS |
| `python scripts/run_h3_os_package_live_probe.py --source-id debian_snapshot --request-key example_package_metadata --check` | PASS, blocked before network because committed live approval is missing |
| `python scripts/summarize_h3_os_package_live_probe_outputs.py --input examples/connectors/h3_os_package_archives/live_probe_results --check` | PASS |
| `python -m unittest tests.connectors.test_h3_os_package_live_probe tests.operations.test_h3_os_package_live_probe_scripts` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS with existing informational warnings |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS with existing review-packet path warnings |
| `py -3 .aide/scripts/aide_lite.py test` | PASS |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS |
| `py -3 .aide/scripts/aide_lite.py verify` | PASS with expected diff-scope warnings while H3-BUNDLE-03 files were uncommitted |
| `py -3 .aide/scripts/aide_lite.py adapter validate` | PASS |

The full `python -m unittest discover -s tests -t .` run was interrupted by the operator before the H3-BUNDLE-04 redirect. A failing IA readiness lane found before interruption was repaired by preserving `HUMAN-OBS-REVIEW-01` in the latest task packet, and `python scripts/validate_ia_readiness_polish.py` plus `python -m unittest tests.operations.test_ia_readiness_polish` passed after that repair.

Current generated scope records no network, no repository index sync, no downloads, no package-manager invocation, no installs, and no execution.
