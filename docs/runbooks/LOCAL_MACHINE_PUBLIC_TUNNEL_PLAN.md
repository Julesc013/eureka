# Local Machine Public Tunnel Plan

This runbook is for `LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00`.

## What This Does

- Builds a reversible exposure plan for the read-only public alpha.
- Consumes the completed public-alpha ops posture artifact.
- Writes `exposure_plan.json` and `EXPOSURE_PLAN_REPORT.md`.
- Records route allowlists, route denylists, validation steps, future tunnel
  placeholders, and rollback/emergency-disable steps.

## What This Does Not Do

- It does not start the local server.
- It does not start a tunnel or reverse proxy.
- It does not modify DNS, firewall, or router state.
- It does not expose Workbench.
- It does not enable mutation, live metadata, downloads, uploads, or provider
  truth.
- It does not approve launch or claim production readiness.

## Generate The Plan

```powershell
python scripts/eureka_local_machine_public_exposure.py plan `
  --mode reverse_tunnel `
  --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json `
  --out .eureka/public-alpha/exposure/latest
```

## Validate The Plan

```powershell
python scripts/eureka_local_machine_public_exposure.py validate `
  --plan .eureka/public-alpha/exposure/latest/exposure_plan.json `
  --strict
```

## Read Status

```powershell
python scripts/eureka_local_machine_public_exposure.py status `
  --plan .eureka/public-alpha/exposure/latest/exposure_plan.json
```

## Recommended Exposure Mode

Use `reverse_tunnel` unless the operator explicitly chooses `reverse_proxy` or a
LAN-only test. `router_port_forward` and `direct_public_ip` are blocked unless
explicitly approved.

## Local Server Command Template

```powershell
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha
```

The local origin should remain loopback-bound. Public exposure should be a
future tunnel/proxy forwarding to loopback.

## Future Tunnel Placeholder

```powershell
<selected-tunnel-provider> tunnel --url http://127.0.0.1:8765
```

This placeholder is not executable approval. The next task must choose the
provider/public URL and receive explicit operator approval before starting
anything.

## Public Route Allowlist

- `/`
- `/health`
- `/status`
- `/api/status`
- `/about`
- `/method`
- `/search`
- `/api/search`
- `/record/`

## Public Route Denylist

- `/workbench`
- `/workbench/`
- `/review`
- `/review/`
- `/admin`
- `/admin/`
- `/api/review`
- `/api/promote`
- `/api/mutate`
- `/api/index/rebuild`
- `/api/source/live`
- `/api/download`
- `/download`
- `/upload`
- `/api/upload`
- `/debug`
- `/debug/`

## Rollback And Emergency Disable

1. Disable or pause the tunnel/proxy public route.
2. Stop any tunnel/proxy process.
3. Stop the local public-alpha server.
4. Restart only on `127.0.0.1` if needed.

## Remaining Blockers

- Operator public URL/provider choice is missing.
- Provider HTTPS/TLS is not selected or validated.
- Tunnel/proxy rehearsal has not run.
- A known staged record ID is still needed for `/record` route smoke.
- Full discovery launch report is missing.
- Release promotion report is missing.
- Manual public launch approval is missing.

## Next Task

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00
```
