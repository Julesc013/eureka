# Local Review Rebuild Runbook

Initialize and validate an instance:

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

Set an operator token:

```bash
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "<operator-token>" --json
```

Start the local service:

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765 --operator-token "<operator-token>"
```

Smoke the review loop:

```bash
python scripts/eureka_local_review_smoke.py --base-url http://127.0.0.1:8765 --operator-token "<operator-token>" --json
```

CLI examples:

```bash
python scripts/eureka_review_queue.py --instance ./eureka-instance --json list
python scripts/eureka_review_queue.py --instance ./eureka-instance --json show --id <review_item_id>
python scripts/eureka_review_queue.py --instance ./eureka-instance --json decide --id <review_item_id> --decision accept --operator-token "<operator-token>" --local-only-confirmed
python scripts/eureka_rebuild_reviewed_index.py --instance ./eureka-instance --operator-token "<operator-token>" --apply --json
```

Do not commit `eureka-instance/**` or operator tokens.
