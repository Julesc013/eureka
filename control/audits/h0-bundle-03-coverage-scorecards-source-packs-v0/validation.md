# Validation

Validation was run offline. Core H0-BUNDLE-03 validators and tests pass. AIDE
`verify` returned WARN with zero errors for pre-existing missing optional
references in `.aide/context/latest-review-packet.md`.

```powershell
python scripts/validate_source_os_coverage_scorecards.py
python scripts/audit_h0_integration.py --check
python -m unittest tests.connectors.test_source_os_coverage_scorecards
python -m unittest tests.operations.test_source_os_coverage_scorecard_scripts
python -m unittest tests.operations.test_h0_integration_audit
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

Additional inherited IA/H0/core validators and AIDE Lite doctor, validate,
test, selftest, eval list, eval run, review-pack, and adapter validate were run.
