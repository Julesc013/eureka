# Local Operator Auth

LOCAL-08 uses a local operator token for review and rebuild mutations.

Configure a token:

```bash
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "<operator-token>" --json
```

The script stores `config/operator.json` with a salt and token hash. It does not
store the raw token and does not print it.

The local server can also receive an in-memory token:

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765 --operator-token "<operator-token>"
```

This remains localhost-only. LAN operator access is not enabled.
