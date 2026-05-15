# LOCAL Clean-Machine Smoke Test

LOCAL-13 smoke starts the local service on `127.0.0.1`, runs service smoke, HTML workbench smoke, auto-test, auto-search, and then shuts the server down.

Run:

```powershell
python scripts/eureka_clean_machine_smoke.py --repo . --instance ./eureka-instance --json
```

The instance path is explicit and must remain uncommitted. The smoke does not use LAN, source probes, extraction, model/provider calls, downloads, installation, deployment, `site/dist`, or master-index mutation.
