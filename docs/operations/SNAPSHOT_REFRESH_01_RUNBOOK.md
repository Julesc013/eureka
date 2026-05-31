# SNAPSHOT-REFRESH-01 Runbook

Use the live metadata refresh after `LIVE-METADATA-PILOT-BATCH-00` has passed.

```powershell
python scripts/eureka_snapshot_refresh.py --from-live-metadata-pilot-examples --json
python scripts/eureka_snapshot_refresh.py --from-live-metadata-pilot-examples --write-examples --json
python scripts/eureka_snapshot_refresh_report.py --from-live-metadata-examples --json
python scripts/validate_snapshot_refresh.py
```

The commands read committed redacted examples only. They do not call live
sources, write `site/dist`, mutate indexes, download, extract, deploy, or
publish.
