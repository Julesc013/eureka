# Search Hunt UI Runbook

Initialize a local instance and create a sample hunt:

```powershell
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_search_hunt.py --instance ./eureka-instance create --query "sampleproject" --json
```

Start the local service:

```powershell
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765
```

Open:

- `http://127.0.0.1:8765/hunts`
- `http://127.0.0.1:8765/api/v1/hunts`

Smoke test:

```powershell
python scripts/eureka_search_hunt_ui_smoke.py --base-url http://127.0.0.1:8765 --instance ./eureka-instance --json
```

The smoke checks loopback routes only and does not perform source probes, model calls, WorkUnit execution, review mutation, index rebuild, deployment, or public launch work.

