# Local Machine Public Tunnel Operator Input

This runbook records the safe handoff point after remote sync is resolved and
before any public tunnel rehearsal starts.

## Current State

The operator-choice artifact can be generated, but it remains blocked until an
operator supplies a real provider name and HTTPS public URL.

Current blocked placeholder values:

```text
provider_name = OPERATOR_REQUIRED
public_url = OPERATOR_REQUIRED
```

Generated artifact location:

```text
.eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
.eureka/public-alpha/exposure/operator-choice/latest/OPERATOR_CHOICE_REPORT.md
```

These files are ignored local state. Do not force-add them unless a later task
explicitly changes the repo convention.

## Required Operator Inputs

Before tunnel rehearsal, provide:

- Provider name, such as `cloudflare_tunnel`, `tailscale_funnel`, `ngrok`, or another reviewed provider value accepted by the CLI.
- HTTPS public URL for the provider-managed tunnel.
- Optional provider dashboard URL, if useful for operator notes.
- Staged record ID for future `/record/...` smoke, if it changes from the existing staging bundle.

The current staged record ID found in the local public staging bundle is:

```text
local-reviewed-record:1792f5ba3d54774c
```

## Safe Regeneration Command

This command records operator input only. It must not start a local server,
tunnel, proxy, DNS change, firewall change, router change, or launch approval.

```powershell
python scripts/eureka_local_machine_public_exposure.py choose `
  --plan .eureka/public-alpha/exposure/latest/exposure_plan.json `
  --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json `
  --mode reverse_tunnel `
  --provider-class provider_managed_https_tunnel `
  --provider-name <provider-name> `
  --public-url https://<provider-public-url> `
  --staged-record-id local-reviewed-record:1792f5ba3d54774c `
  --out .eureka/public-alpha/exposure/operator-choice/latest
```

Then validate:

```powershell
python scripts/eureka_local_machine_public_exposure.py validate-choice --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json --strict
python scripts/eureka_local_machine_public_exposure.py choice-status --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
```

## Expected Advancement

If the provider name, HTTPS public URL, staged record ID, and remote-sync state
are all valid, the generated choice may advance to:

```text
READY_FOR_TUNNEL_REHEARSAL
```

That status still does not start exposure. It only unblocks the next explicit
tunnel rehearsal task.

## Safety Rules

- Do not start a tunnel or reverse proxy from this task.
- Do not expose Workbench.
- Do not enable public mutation.
- Do not enable downloads, uploads, live metadata, source fetching, extraction, or install emulation.
- Do not change DNS, firewall, or router settings.
- Do not create launch approval.
- Do not mutate `.aide/queue/`.
- Do not claim release readiness or full discovery.
