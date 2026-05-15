# SearchNeed Runbook

Initialize an instance:

```powershell
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "local-dev-token" --json
```

Create a hunt and SearchNeed:

```powershell
python scripts/eureka_search_hunt.py --instance ./eureka-instance create --query "sampleproject" --json
python scripts/eureka_hunt_to_search_need.py --instance ./eureka-instance --operator-token "local-dev-token" --hunt-id <hunt_id> --json
python scripts/eureka_search_need.py --instance ./eureka-instance list --json
```

The local instance path remains ignored local state. Do not commit operator tokens.
