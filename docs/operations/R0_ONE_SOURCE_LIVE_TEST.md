# R0 One Source Live Test

Dry-run without network:

```powershell
python scripts/run_one_source_live_test.py --package-name sampleproject --source-cache-db control/audits/r0-09-one-source-live-test-v0/generated/source_cache_live.sqlite --evidence-db control/audits/r0-09-one-source-live-test-v0/generated/evidence_live.sqlite --review-db control/audits/r0-09-one-source-live-test-v0/generated/review_live.sqlite --public-index-db control/audits/r0-09-one-source-live-test-v0/generated/public_index_live.sqlite --output control/audits/r0-09-one-source-live-test-v0/generated/sample_live_test_output.json --json
```

Live one-request metadata run:

```powershell
python scripts/run_one_source_live_test.py --live --package-name sampleproject --source-cache-db control/audits/r0-09-one-source-live-test-v0/generated/source_cache_live.sqlite --evidence-db control/audits/r0-09-one-source-live-test-v0/generated/evidence_live.sqlite --review-db control/audits/r0-09-one-source-live-test-v0/generated/review_live.sqlite --public-index-db control/audits/r0-09-one-source-live-test-v0/generated/public_index_live.sqlite --decision accept --search-query sampleproject --absence-query definitely-not-sampleproject-r0-missing-query --output control/audits/r0-09-one-source-live-test-v0/generated/sample_live_test_output.json --json
```

Validation:

```powershell
python scripts/validate_one_source_live_test.py --require-live
```

Generated SQLite databases can be inspected with standard SQLite tools. The important tables are the source cache entries, evidence candidates, review decisions, and reviewed public index records.

Search success means the accepted local review record is findable in the local reviewed index. The absence report only says the local reviewed index had no matching record for the missing query.

F0 remains blocked because this is a one-source gate, not production launch. R0-10 is next because dev-to-main promotion needs a production review across the recovered runtime seams and remaining governance blockers.
