# Local Apply Live Metadata Previews Runbook

Use the default temp-only flow:

```text
python scripts/eureka_local_apply_preview_validate.py --from-live-metadata-review-examples --json
python scripts/eureka_local_apply_live_metadata_previews.py --from-live-metadata-review-examples --use-temp-instance --json
python scripts/eureka_local_apply_live_metadata_report.py --from-examples --json
```

The temp apply proof must show:

- one reviewed metadata record created
- two reviewed source leads created
- rollback plan created
- no operator instance mutation
- no public or master index mutation
- no verified-download, malware-clean, rights-clearance, or artifact-verified claim

Operator instance apply is not part of this task. A future operator-instance
apply would require explicit approval, an operator token, backup evidence,
rollback evidence, and an affected-path report.
