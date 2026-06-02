# Snapshot Refresh 04 Runbook

Use the deterministic examples lane:

```bash
python scripts/eureka_snapshot_refresh.py --from-manuals-driver-examples --json
python scripts/eureka_snapshot_refresh.py --from-manuals-driver-examples --write-examples --json
python scripts/eureka_snapshot_refresh_report.py --from-manuals-driver-examples --json
python scripts/validate_snapshot_refresh.py
```

Do not deploy, write `site/dist`, mutate reviewed/master/public indexes, fetch
documents, fetch driver packages, OCR, extract, install, execute, call model
providers, or claim production/public launch readiness.

Expected counts:

- manuals/scans candidates: 16
- driver/support candidates: 16
- additional seed candidates: 32
- total limited reviewed projection count: 4
- total candidates after live metadata: 68
