# Search Hunt Command Runbook

Initialize an explicit local instance and configure an operator token:

```powershell
$Workspace = "D:\Projects\Eureka"
$Instance = "$Workspace\instances\default"
$Token = "local-dev-token"

python scripts/eureka_init_instance.py --instance $Instance --json
python scripts/eureka_set_operator_token.py --instance $Instance --token $Token --json
```

Create a hunt, then apply commands:

```powershell
python scripts/eureka_search_hunt.py --instance $Instance create --query "sampleproject" --json
python scripts/eureka_search_hunt_command.py --instance $Instance --operator-token $Token pause --id <hunt_id> --reason "operator pause" --json
python scripts/eureka_search_hunt_command.py --instance $Instance --operator-token $Token resume --id <hunt_id> --reason "operator resume" --json
python scripts/eureka_search_hunt_command.py --instance $Instance --operator-token $Token steer --id <hunt_id> --type metadata_only --reason "keep future work bounded" --json
```

Read history without a token:

```powershell
python scripts/eureka_search_hunt_command.py --instance $Instance commands --id <hunt_id> --json
python scripts/eureka_search_hunt_command.py --instance $Instance steering --id <hunt_id> --include-inactive --json
```

The demo script exercises pause/resume, steering, deactivation, command history, and invalid-command rejection:

```powershell
python scripts/demo_search_hunt_commands.py --instance $Instance --operator-token $Token --json
```
