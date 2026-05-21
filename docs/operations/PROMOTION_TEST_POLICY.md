# Promotion Test Policy

Promotion requires full validation:

- branch and clean-tree checks
- L0/L1/L2 selected tests
- L3 full unittest discovery
- L4 promotion/release checks
- all relevant validators
- no active blocking failure-ledger entries

`scripts/eureka_test_select.py --promotion --json` must include:

- `python -m unittest discover -s tests -t .`
- `full_discovery_required: true`
- `promotion_allowed: false` when active blocking failures remain

Per-commit selected lanes may defer full discovery, but promotion may not.

