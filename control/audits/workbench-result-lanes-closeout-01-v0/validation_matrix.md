# Validation Matrix

| Lane | Command group | Result |
| --- | --- | --- |
| Failed-first | Original Search Hunt ledger reruns | PASS |
| Focused result-lane | Workbench result-lane validators, smokes, and unit tests | PASS |
| Global | `git diff --check` | PASS |
| Global | Architecture boundaries | PASS |
| Global | AIDE doctor, validate, test, selftest, verify, review-pack | PASS |
| Global | Generated artifact cleanliness | FAIL before commit because the audit pack is uncommitted generated drift |
| Full discovery | `python -m unittest discover -s tests -t .` | FAIL |
| Targeted repair | `python -m unittest tests.operations.test_local_appliance_track` after repo-health update | PASS |
| Targeted reproduction | `python -m unittest tests.operations.test_contract_taxonomy_plan` | FAIL |
