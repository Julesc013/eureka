# Local LAN Read-Only Smoke Test

LOCAL-12 proves explicit LAN mode can serve read-only local appliance routes
without opening mutation paths.

## Same-Machine Smoke

```powershell
python scripts/eureka_lan_smoke.py --instance ./eureka-instance --host 0.0.0.0 --port 8765 --bind-lan --read-only --json
```

The script initializes the explicit instance if needed, starts the local service
with `--bind-lan`, probes read-only routes through `127.0.0.1`, validates LAN
mutation blocking through the route gate, shuts the server down, and validates
the instance after shutdown.

Same-machine smoke is useful proof of bind/read-only behavior, but it is not
cross-device proof.

## Read-Only Probe

```powershell
python scripts/eureka_lan_read_only_probe.py --base-url http://127.0.0.1:8765 --json
```

The probe refuses public internet hostnames. It allows localhost, loopback, and
private LAN addresses only. It checks status, health, search, absence, home, and
API routes, then verifies mutation routes are rejected or token-gated.

## Boundaries

- no deployment
- no public hosting claim
- no source probes
- no WorkUnit execution from LAN
- no review/rebuild mutation from LAN
- no master-index mutation
- no production readiness claim
- no public launch claim
