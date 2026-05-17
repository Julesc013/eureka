# Search Hunt Runtime Runbook

Initialize and validate a local instance:

```powershell
$Workspace = "D:\Projects\Eureka"
$Instance = "$Workspace\instances\default"

python scripts/eureka_init_instance.py --instance $Instance --json
python scripts/eureka_validate_instance.py --instance $Instance --json
```

Create and inspect a session:

```powershell
python scripts/eureka_search_hunt.py --instance $Instance create --query "sampleproject" --json
python scripts/eureka_search_hunt.py --instance $Instance list --json
python scripts/eureka_search_hunt.py --instance $Instance show --id <session-id> --with-transitions --with-summaries --json
```

Record a basic state transition:

```powershell
python scripts/eureka_search_hunt.py --instance $Instance transition --id <session-id> --state running --reason "operator inspection" --json
```

Run the demo and validator:

```powershell
python scripts/demo_search_hunt_session.py --instance $Instance --query "sampleproject" --json
python scripts/validate_search_hunt_runtime.py
```

HUNT-01 remains local-only. It does not create WorkUnits, run source probes, use model providers, mutate review decisions, rebuild indexes, deploy, or claim production/public launch readiness.
