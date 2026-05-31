# Live Metadata Pilot Runbook

Default modes are safe and require no approval:

```powershell
python scripts/eureka_live_metadata_pilot_approval.py --template --json
python scripts/eureka_live_metadata_pilot_batch.py --dry-run --json
python scripts/eureka_live_metadata_pilot_batch.py --fixture --json
python scripts/eureka_live_metadata_pilot_report.py --from-examples --json
```

To write deterministic examples and evidence:

```powershell
python scripts/eureka_live_metadata_pilot_batch.py --fixture --write-examples --json
```

Approved live mode requires:

```powershell
python scripts/eureka_live_metadata_pilot_batch.py --operator-approved-live-metadata --approval control/approvals/live-metadata-pilot-batch-00-approval.json --json
```

Do not run live mode unless the approval file exists and contains the exact
approval phrase.
