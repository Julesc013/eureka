# SNAPSHOT-REFRESH-03 Runbook

Run the refresh from committed examples:

```powershell
python scripts/eureka_snapshot_refresh.py --from-local-apply-live-metadata-examples --json
python scripts/eureka_snapshot_refresh.py --from-local-apply-live-metadata-examples --write-examples --json
python scripts/eureka_snapshot_refresh_report.py --from-local-apply-live-metadata-examples --json
```

Then run focused validation:

```powershell
python scripts/validate_snapshot_refresh.py
python -m unittest tests.runtime.test_snapshot_refresh_local_apply_section
python -m unittest tests.runtime.test_snapshot_refresh_reviewed_metadata_records
python -m unittest tests.runtime.test_snapshot_refresh_reviewed_source_leads
```

Do not deploy, write `site/dist`, mutate public/master indexes, mutate operator instances, call live sources, download, extract, execute, install, or make readiness claims.
