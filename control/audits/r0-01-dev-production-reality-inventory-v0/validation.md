# Validation

R0-01 validation state:

- `git status --short`: `pass_expected_r0_changes`
- `git diff --check`: `pass`
- `python scripts/audit_dev_production_reality.py --check --json`: `pass`
- `python scripts/audit_dev_production_reality.py --output control/audits/r0-01-dev-production-reality-inventory-v0/generated/sample_artifact_inventory.json --summary-output control/audits/r0-01-dev-production-reality-inventory-v0/generated/sample_summary.md`: `pass`
- `python scripts/validate_dev_production_reality.py`: `pass`
- `python -m unittest tests.operations.test_dev_production_reality`: `pass`
- `python -m unittest discover -s tests -t .`: `pass`
- `python scripts/check_architecture_boundaries.py`: `pass`
- `py -3 .aide/scripts/aide_lite.py doctor`: `pass`
- `py -3 .aide/scripts/aide_lite.py validate`: `pass`
- `py -3 .aide/scripts/aide_lite.py test`: `pass`
- `py -3 .aide/scripts/aide_lite.py selftest`: `pass`
- `py -3 .aide/scripts/aide_lite.py verify`: `warn_no_errors`
- `py -3 .aide/scripts/aide_lite.py review-pack`: `pass`

Boundary confirmations:

- Network/API/model/provider calls: `not_used`
- Source discovery/sync/downloads: `not_used`
- Source cache/evidence ledger/review queue/public index mutation: `not_used`
- F0 continuation: `blocked`
- dev-to-main promotion: `blocked`
