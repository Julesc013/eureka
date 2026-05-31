# Snapshot Refresh Runbook

Fixture refresh:

```bash
python scripts/eureka_snapshot_refresh.py --from-seed-examples --json
```

Refresh and write public-safe examples:

```bash
python scripts/eureka_snapshot_refresh.py --from-seed-examples --write-examples --json
```

Report from examples:

```bash
python scripts/eureka_snapshot_refresh_report.py --from-examples --json
```

This runbook does not write `site/dist`, mutate `data/public_index`, deploy,
publish, download, extract, call model providers, or create launch readiness
claims.
