# SNAPSHOT-REFRESH-02 Runbook

Run the example-only refresh:

```bash
python scripts/eureka_snapshot_refresh.py --from-live-metadata-review-examples --json
```

Regenerate public-safe examples and inventory:

```bash
python scripts/eureka_snapshot_refresh.py --from-live-metadata-review-examples --write-examples --json
```

Then validate with the focused snapshot validator and related guard validators. Do not run full unittest discovery inside the AI session.

The runbook does not permit deployment, publishing, live calls, downloads, extraction, public mutation, or reviewed-index mutation.
