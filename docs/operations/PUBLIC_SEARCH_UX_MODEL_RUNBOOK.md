# Public Search UX Model Runbook

Build the example bundle:

```powershell
python scripts/eureka_public_search_ux_model.py --from-snapshot-refresh-examples --json
```

Refresh public-safe examples:

```powershell
python scripts/eureka_public_search_ux_model.py --from-snapshot-refresh-examples --write-examples --json
```

Validate:

```powershell
python scripts/validate_public_search_ux_model.py
```

The runbook does not start a server, deploy, publish, write public indexes, call
live sources, download, extract, or use model providers.
