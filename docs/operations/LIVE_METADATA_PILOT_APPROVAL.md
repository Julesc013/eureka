# Live Metadata Pilot Approval

The approval file must be written by an operator before any live metadata call.

Accepted path:

```text
control/approvals/live-metadata-pilot-batch-00-approval.json
```

Required phrase:

```text
RUN_BOUNDED_LIVE_METADATA_PILOT
```

Required boundaries:

- metadata only
- no raw response commit
- no downloads
- no extraction
- no public mutation
- no accepted truth
- review required

The approval template is available from:

```powershell
python scripts/eureka_live_metadata_pilot_approval.py --template --json
```
