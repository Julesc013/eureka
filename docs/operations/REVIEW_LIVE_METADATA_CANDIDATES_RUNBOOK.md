# Review Live Metadata Candidates Runbook

Use the deterministic, example-backed mode:

```bash
python scripts/eureka_review_live_metadata_candidates.py --from-live-metadata-examples --json
python scripts/eureka_live_metadata_promotion_preview.py --from-live-metadata-examples --json
python scripts/eureka_live_metadata_local_apply_handoff.py --from-live-metadata-examples --json
python scripts/eureka_live_metadata_review_report.py --from-examples --json
```

To refresh examples, inventory, and audit evidence:

```bash
python scripts/eureka_review_live_metadata_candidates.py --from-live-metadata-examples --write-examples --json
```

Do not run this task as a live source probe. It consumes existing redacted summaries only.
