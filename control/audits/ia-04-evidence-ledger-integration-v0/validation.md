# Validation

Required IA prerequisite validators passed before IA-04 implementation:

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- `python scripts/validate_ia_source_cache_write.py`

IA-04 focused validation lanes:

- `python scripts/validate_ia_evidence_ledger_integration.py`
- `python scripts/eureka_ia_evidence_ledger_write.py --instance <temp-instance> --operator-token local-dev-token --from-source-cache --dry-run --json`
- `python -m unittest tests.runtime.test_ia_evidence_ledger_integration`
- `python -m unittest tests.runtime.test_ia_evidence_records`
- `python -m unittest tests.runtime.test_ia_evidence_boundaries`
- `python -m unittest tests.operations.test_ia_evidence_ledger_scripts`
