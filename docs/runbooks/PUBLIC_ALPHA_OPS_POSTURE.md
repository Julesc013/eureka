# Public Alpha Ops Posture

This runbook is for `PUBLIC-ALPHA-OPS-POSTURE-00`.

## What This Does

- Generates a conservative read-only public-alpha operations posture.
- Writes `ops_posture.json` and `OPS_POSTURE_REPORT.md`.
- Validates that public mutation, Workbench exposure, live metadata, downloads,
  uploads, model/provider truth, public exposure, and production-readiness claims
  remain off.
- Provides fields that the local-machine public exposure planner can consume.

## What This Does Not Do

- It does not launch Eureka.
- It does not start a tunnel, proxy, DNS change, firewall change, or public URL.
- It does not expose Workbench.
- It does not enable downloads, uploads, live metadata, accounts, telemetry, or
  public mutation.
- It does not run full discovery or release promotion.
- It does not approve public launch.

## Commands

Generate the posture:

```powershell
python scripts/eureka_public_alpha_ops_posture.py plan --out .eureka/ops/public-alpha/latest
```

Validate it:

```powershell
python scripts/eureka_public_alpha_ops_posture.py validate --plan .eureka/ops/public-alpha/latest/ops_posture.json
```

Check status:

```powershell
python scripts/eureka_public_alpha_ops_posture.py status --plan .eureka/ops/public-alpha/latest/ops_posture.json
```

Render the report again if needed:

```powershell
python scripts/eureka_public_alpha_ops_posture.py report --plan .eureka/ops/public-alpha/latest/ops_posture.json
```

## Exposure Plan Input

After the posture validates, the exposure planner can consume it:

```powershell
python scripts/eureka_local_machine_public_exposure.py plan `
  --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json `
  --release-check-report .eureka/release-checks/public-alpha/latest/release_check_report.json `
  --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json `
  --exposure-mode reverse_tunnel `
  --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json `
  --out .eureka/public-alpha/exposure/latest
```

## Safe Defaults

- Public alpha is read-only.
- Public no-auth is selected only for the read-only public surface.
- Operator/Workbench routes remain blocked from public exposure.
- Public exposure remains disabled.
- Rate limit, logging, monitoring, rollback, and report/takedown posture are
  configured as alpha requirements.
- Report/takedown defaults to the repository issue channel.

## Remaining Blockers

The generated posture can be `READY_FOR_EXPOSURE_PLAN`, but launch still remains
blocked until public exposure, public URL, HTTPS/TLS or tunnel provider HTTPS,
full discovery, release promotion, and manual launch approval pass.

## Rollback Expectation

For public alpha, rollback means disabling the public tunnel/proxy route first,
then stopping the local public-alpha server, then restarting only on loopback.

## Structure Guardrail

The current root structure is accepted. This task does not create new top-level
roots. Ops posture belongs under `runtime/local`, `scripts`, `docs/runbooks`,
`control/audits`, and ignored generated `.eureka/ops` output. AIDE/control
artifacts remain guardrails and evidence, not product runtime truth.

## Next Task After PASS

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00
```
