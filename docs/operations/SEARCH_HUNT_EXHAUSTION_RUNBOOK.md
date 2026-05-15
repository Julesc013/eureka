# Search Hunt Exhaustion Runbook

Initialize a local instance:

```powershell
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "local-dev-token" --json
```

Create a sample hunt and generate a report:

```powershell
python scripts/eureka_search_hunt.py --instance ./eureka-instance create --query "sampleproject" --json
python scripts/eureka_search_hunt_exhaustion.py --instance ./eureka-instance --operator-token "local-dev-token" --id <hunt_id> --generate --json
python scripts/eureka_search_hunt_exhaustion.py --instance ./eureka-instance --id <hunt_id> --show --json
```

The demo script performs the same proof and checks that WorkUnit and public-index summaries are unchanged:

```powershell
python scripts/demo_search_hunt_exhaustion.py --instance ./eureka-instance --operator-token "local-dev-token" --query "sampleproject" --json
```

Use the local workbench route `/hunt/<hunt_id>` to inspect the latest report, checked layers, deferred layers, blocked policy entries, recommended future action categories, and non-claims.
