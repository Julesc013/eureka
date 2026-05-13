# Local LAN Safety Gate

LOCAL-11 adds the fail-closed guard for read-only LAN mode.

## Check Policy

```powershell
python scripts/eureka_lan_policy_check.py --host 127.0.0.1 --json
python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --json
python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --bind-lan --json
```

The second command should report `host_allowed: false` while still exiting
successfully as a policy report.

## Start With LAN Binding

LOCAL-11 permits the code path but does not require actual LAN smoke:

```powershell
python scripts/eureka_local_server.py --instance ./eureka-instance --host 0.0.0.0 --port 8765 --bind-lan --json-startup
```

Use Ctrl+C to stop the service. Confirm no local instance state is committed.

## Safety Rules

- localhost remains the default
- `--bind-lan` is required for all-interface bind hosts
- LAN clients are read-only
- operator mutations remain localhost-only
- no source probes, WorkUnit execution, extraction, agents, deployment, or public hosting claim
