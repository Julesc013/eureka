# Public Alpha No Deployment Policy

This bundle forbids deployment, launch, provider calls, DNS changes, generated site output mutation, secrets, public bind, live fanout, uploads, accounts, telemetry, downloads, execution, public relay, and index mutation.

## Current Boundary

- Planning is not deployment.
- Operator signoff for deployment execution is absent.
- No provider API call, DNS change, generated site output mutation, provider credential, secret, public bind, public alpha live claim, or production claim is made.
- Downloads, uploads, accounts, telemetry, live source fanout, source sync, public relay, install, execute, mirror, emulation, public index writes, and master index writes remain disabled.

## Validation

- `python scripts/validate_public_alpha_deployment_plan.py`
- `python scripts/check_public_alpha_deployment_plan.py --input examples/hosting/deployment/public_alpha_deployment_plan_v0.json --check`
- `python scripts/check_public_alpha_config_manifest.py --input examples/hosting/deployment/public_alpha_config_manifest_v0.json --check`
- `python scripts/check_public_alpha_dns_readiness.py --input examples/hosting/deployment/public_alpha_dns_readiness_unknown_v0.json --check`
