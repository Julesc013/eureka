# TRACK-A-01 Validation Evidence

Final observed results:

- `git status --short`: PASS with expected changed files before commit
- `git diff --check`: PASS
- `git check-ignore .aide.local/`: PASS
- `python -m json.tool control/inventory/publication/host_profiles.json`: PASS
- `python -m json.tool control/inventory/publication/representation_profiles.json`: PASS
- `python -m json.tool control/inventory/publication/capability_negotiation_policy.json`: PASS
- `python -m json.tool control/audits/track-a-01-representation-contracts-v0/track_a_01_report.json`: PASS
- `python scripts/validate_representation_contracts.py`: PASS
- `python scripts/validate_repository_layout.py --json`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `python -m unittest tests.contracts.test_representation_contracts`: PASS
- `python -m unittest tests.scripts.test_validate_repository_layout`: PASS after narrow validator guard alignment
- `python -m unittest discover -s tests -t .`: PASS, 1578 tests
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 0 errors
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 14/14, no provider/model/network calls
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS packet generation, verifier result WARN
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS
- strict secret scan over changed paths: PASS

The WARN-only AIDE verifier state is documented in
`control/audits/track-a-01-representation-contracts-v0/validation.md`.
