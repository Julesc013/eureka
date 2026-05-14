# Search Hunt Command Runbook

Initialize an explicit local instance and configure an operator token:

```powershell
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "local-dev-token" --json
```

Create a hunt, then apply commands:

```powershell
python scripts/eureka_search_hunt.py --instance ./eureka-instance create --query "sampleproject" --json
python scripts/eureka_search_hunt_command.py --instance ./eureka-instance --operator-token "local-dev-token" pause --id <hunt_id> --reason "operator pause" --json
python scripts/eureka_search_hunt_command.py --instance ./eureka-instance --operator-token "local-dev-token" resume --id <hunt_id> --reason "operator resume" --json
python scripts/eureka_search_hunt_command.py --instance ./eureka-instance --operator-token "local-dev-token" steer --id <hunt_id> --type metadata_only --reason "keep future work bounded" --json
```

Read history without a token:

```powershell
python scripts/eureka_search_hunt_command.py --instance ./eureka-instance commands --id <hunt_id> --json
python scripts/eureka_search_hunt_command.py --instance ./eureka-instance steering --id <hunt_id> --include-inactive --json
```

The demo script exercises pause/resume, steering, deactivation, command history, and invalid-command rejection:

```powershell
python scripts/demo_search_hunt_commands.py --instance ./eureka-instance --operator-token "local-dev-token" --json
```
