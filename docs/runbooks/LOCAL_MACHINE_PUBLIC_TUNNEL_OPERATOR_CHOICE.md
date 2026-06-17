# Local Machine Public Tunnel Operator Choice

This runbook is for `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00`.

## What This Does

- Records the operator's exposure mechanism choice before any tunnel rehearsal.
- Consumes the public-alpha ops posture and exposure plan artifacts.
- Writes `operator_choice.json` and `OPERATOR_CHOICE_REPORT.md`.
- Checks remote sync posture so public exposure rehearsal does not happen from
  an unpushed local commit by accident.

## What This Does Not Do

- It does not start the local server.
- It does not start a tunnel or reverse proxy.
- It does not activate a public URL.
- It does not modify DNS, firewall, or router state.
- It does not expose Workbench, mutation, live metadata, downloads, or uploads.
- It does not approve launch or claim production readiness.

## Generate The Choice

```powershell
python scripts/eureka_local_machine_public_exposure.py choose `
  --plan .eureka/public-alpha/exposure/latest/exposure_plan.json `
  --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json `
  --mode reverse_tunnel `
  --provider-class provider_managed_https_tunnel `
  --provider-name OPERATOR_REQUIRED `
  --public-url OPERATOR_REQUIRED `
  --out .eureka/public-alpha/exposure/operator-choice/latest
```

## Validate The Choice

```powershell
python scripts/eureka_local_machine_public_exposure.py validate-choice `
  --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json `
  --strict
```

## Read Choice Status

```powershell
python scripts/eureka_local_machine_public_exposure.py choice-status `
  --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
```

## Supplying Provider And URL

Use the same command with a real provider name and HTTPS public URL:

```powershell
python scripts/eureka_local_machine_public_exposure.py choose `
  --plan .eureka/public-alpha/exposure/latest/exposure_plan.json `
  --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json `
  --mode reverse_tunnel `
  --provider-class provider_managed_https_tunnel `
  --provider-name ngrok `
  --public-url https://example-public-alpha-url.invalid `
  --staged-record-id <reviewed-record-id> `
  --confirm-remote-synced `
  --out .eureka/public-alpha/exposure/operator-choice/latest
```

Provider classes:

- `provider_managed_https_tunnel`
- `self_managed_reverse_proxy`
- `private_lan_rehearsal`
- `router_port_forward_risky`
- `direct_public_ip_risky`

Provider names are operator supplied, for example `cloudflare_tunnel`,
`tailscale_funnel`, `ngrok`, `caddy_reverse_proxy`, `nginx_reverse_proxy`, or
`other`.

## Remote Sync Requirement

Before `LOCAL-MACHINE-PUBLIC-TUNNEL-00`, `dev` should be pushed to `origin/dev`.
If local `dev` is ahead, the choice status must record `REMOTE_SYNC_REQUIRED`.
Do not silently push from this task.

## Route Safety

Allowed public routes:

- `/`
- `/health`
- `/status`
- `/api/status`
- `/about`
- `/method`
- `/search`
- `/api/search`
- `/record/`

Blocked public routes:

- `/workbench`
- `/review`
- `/admin`
- `/api/review`
- `/api/promote`
- `/api/mutate`
- `/api/index/rebuild`
- `/api/source/live`
- `/download`
- `/upload`
- `/debug`

## Rollback And Emergency Disable

1. Disable or pause the tunnel/proxy public route.
2. Stop any tunnel/proxy process.
3. Stop the local public-alpha server.
4. Restart only on `127.0.0.1`.

## Remaining Blockers

With the default `OPERATOR_REQUIRED` choice, the next blocker is the real tunnel
provider and public HTTPS URL. A staged record ID is also needed for future
`/record/{id}` smoke.

## Next Task

If provider/URL remain missing:

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00
```

If provider/URL are chosen but local `dev` is ahead of `origin/dev`:

```text
REMOTE-SYNC-BEFORE-PUBLIC-EXPOSURE-00
```

If provider/URL are chosen and remote sync is clean:

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-00
```
