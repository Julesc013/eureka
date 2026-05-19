# Validation

Closeout validation lane:

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- `python scripts/validate_ia_source_cache_write.py`
- `python scripts/validate_ia_evidence_ledger_integration.py`
- `python scripts/validate_ia_candidate_index_integration.py`
- `python scripts/validate_ia_review_promotion_dry_run.py`
- `python scripts/validate_ia_reviewed_index_rebuild.py`
- `python scripts/validate_ia_pilot_closeout.py`
- focused IA pilot closeout tests
- architecture boundary check
- generated artifact cleanliness check
- AIDE Lite checks

Full unittest discovery was run with:

`python -m unittest discover -s tests -t .`

Result: non-blocking broad discovery failure. The run executed 4717 tests in
2983.319s and finished with 9 failures and 5 errors. The failing/erroring lanes
were outside the IA closeout focused lane:

- candidate-index contract validators
- HUNT main-promotion state expectations
- R0 runtime leakage gates
- source-observation validation broad gate

The IA-00 through IA-07 validators, IA pilot closeout validator, focused IA
closeout tests, architecture boundary check, and AIDE Lite checks passed. This
does not create a production/public launch claim.
