# LOCAL Clean-Machine Bootstrap

LOCAL-13 proves the Local Appliance can bootstrap from a clean temp checkout/copy.

Run:

```powershell
python scripts/eureka_clean_machine_bootstrap.py --repo . --json
```

The script creates a filtered temp checkout, skips forbidden local state such as `eureka-instance/`, `.aide.local/`, `.cache/`, `.local/`, `secrets/`, and `.env`, initializes an explicit instance, validates it, and checks runtime status.

This proof is local reproducibility evidence only. It is not deployment, production readiness, or public launch readiness.
