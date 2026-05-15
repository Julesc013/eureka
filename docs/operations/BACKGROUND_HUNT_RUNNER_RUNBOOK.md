# Background Hunt Runner Runbook

Initialize an instance, set an operator token, and create a hunt/need/workunit chain:

```text
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "local-dev-token" --json
python scripts/demo_hunt_to_workunits.py --instance ./eureka-instance --operator-token "local-dev-token" --query "sampleproject" --json
```

Plan runner work:

```text
python scripts/eureka_hunt_runner.py --instance ./eureka-instance --hunt-id <hunt_id> plan --json
```

Run one safe local worker:

```text
python scripts/eureka_hunt_runner.py --instance ./eureka-instance --hunt-id <hunt_id> --operator-token "local-dev-token" run-next --json
```

Run a bounded batch:

```text
python scripts/eureka_hunt_runner.py --instance ./eureka-instance --hunt-id <hunt_id> --operator-token "local-dev-token" run-batch --limit 3 --json
```

Validate:

```text
python scripts/validate_background_hunt_runner.py
```

