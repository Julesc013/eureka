# Workbench Live Run Runbook

Create a dry-run packet:

```text
python scripts/eureka_workbench_live_run.py --query sampleproject --projection operator_workbench --dry-run --from-fixtures --include-ia-hunt-dry-run --json
```

Inspect with local service routes:

```text
/runs?q=sampleproject
/api/v1/resolution-runs?q=sampleproject
/api/v1/resolution-runs/{run_id}
/api/v1/resolution-runs/{run_id}/events
/api/v1/resolution-runs/{run_id}/lanes
/api/v1/resolution-runs/{run_id}/workunits
```

Validation:

```text
python scripts/validate_workbench_live_run.py
python -m unittest tests.runtime.test_workbench_live_run
python -m unittest tests.operations.test_workbench_live_run_smoke
```

Operational limits:

- no live IA metadata lane yet
- no source probes
- no store mutation
- no browser review/promote
- no Local Apply Gate
