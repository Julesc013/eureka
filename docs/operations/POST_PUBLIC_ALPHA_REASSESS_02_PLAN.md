# Post Public Alpha Reassess 02 Plan

Recommended next task:

```text
LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00 - Apply eligible live metadata review previews through local apply gate
```

Rationale:

- reviewed record count remains below threshold
- preview records are useful but not applied reviewed records
- local apply is required before any reviewed index mutation
- a later snapshot refresh and public alpha reassessment must follow any apply

Planned after local apply:

- `SNAPSHOT-REFRESH-03`
- `PUBLIC-ALPHA-REASSESS-03`
- `SEED-BATCH-MANUALS-SCANS-00`
- `SEED-BATCH-DRIVER-SUPPORT-00`

The public alpha remains read-only and launch-deferred until reviewed record
coverage improves through the explicit gates.
