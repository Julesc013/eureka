# Public Alpha Static Backend Split

Static hosts serve public-safe static material only. Hosted backend behavior is separate, future, and operator-gated.

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
