# Validation

Primary validation commands:

```powershell
python scripts/validate_ia_metadata_policy.py
python scripts/validate_ia_fixture_replay.py
python scripts/validate_ia_live_metadata_probe.py
python scripts/validate_ia_source_cache_write.py
python scripts/validate_ia_evidence_ledger_integration.py
python scripts/validate_ia_candidate_index_integration.py
python scripts/validate_ia_review_promotion_dry_run.py
python -m unittest tests.runtime.test_ia_review_queue_integration
python -m unittest tests.runtime.test_ia_review_decisions
python -m unittest tests.runtime.test_ia_promotion_dry_run
python -m unittest tests.runtime.test_ia_promotion_boundaries
python -m unittest tests.operations.test_ia_review_promotion_scripts
```

All focused IA-06 checks must pass before IA-06 is reported complete.

