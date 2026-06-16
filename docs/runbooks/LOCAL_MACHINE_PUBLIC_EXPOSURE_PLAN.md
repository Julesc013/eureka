# Local-Machine Public Exposure Plan

This runbook covers `LOCAL-MACHINE-PUBLIC-EXPOSURE-PLAN-00`: deciding how the
current computer could become the public-alpha hosting path without enabling
public exposure yet.

It is not public launch, internet exposure, firewall/router configuration,
DNS/TLS setup, tunnel installation, production auth implementation, release
promotion, full discovery execution, or public mutation.

## Purpose

Use this after local-machine staging passes and the user chooses the current
computer as the hosting path instead of an external SSH staging host.

The task creates a machine-readable plan and report that say:

```text
selected_hosting_path=local_machine
exposure_mode=loopback_only
public_exposure_enabled=false
external_staging_deferred=true
launch_status=BLOCKED
```

This lets release checks and the launch gate stop treating a missing external
SSH host as the next action while still keeping public launch blocked.

## Exposure Modes

Supported planning modes are:

- `none`
- `loopback_only`
- `lan_only`
- `reverse_tunnel`
- `reverse_proxy`
- `router_port_forward`
- `direct_public_ip`

The default is `loopback_only`. It does not make Eureka reachable from the
internet.

## Prerequisites

Validate the local-machine staging report and current gate reports:

```powershell
python scripts/eureka_local_machine_staging.py validate-report --report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json

python scripts/eureka_public_alpha_release_checks.py validate-report --report .eureka/release-checks/public-alpha/latest/release_check_report.json

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

## Plan

```powershell
python scripts/eureka_local_machine_public_exposure.py plan --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --release-check-report .eureka/release-checks/public-alpha/latest/release_check_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/local-machine-public-exposure/public-alpha/latest

python scripts/eureka_local_machine_public_exposure.py validate-plan --plan .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_plan.json

python scripts/eureka_local_machine_public_exposure.py status --plan .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_plan.json
```

The plan writes:

```text
.eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_plan.json
```

Generated `.eureka` files are local ignored artifacts. Do not commit them.

## Report

```powershell
python scripts/eureka_local_machine_public_exposure.py report --plan .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_plan.json --out .eureka/local-machine-public-exposure/public-alpha/latest

python scripts/eureka_local_machine_public_exposure.py validate-report --report .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json
```

The report writes:

```text
.eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json
.eureka/local-machine-public-exposure/public-alpha/latest/LOCAL_MACHINE_PUBLIC_EXPOSURE_REPORT.md
```

Expected status is `PASS_WITH_WARNINGS` because the plan is valid but public
exposure, TLS/domain, auth/no-auth posture, ops posture, release promotion, full
discovery, and launch approval remain blocked.

## Release Checks

Pass the report to release checks:

```powershell
python scripts/eureka_public_alpha_release_checks.py run --bundle .eureka/staging/public-alpha --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --local-machine-public-exposure-report .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/release-checks/public-alpha/latest

python scripts/eureka_public_alpha_release_checks.py validate-report --report .eureka/release-checks/public-alpha/latest/release_check_report.json
python scripts/eureka_public_alpha_release_checks.py status --report .eureka/release-checks/public-alpha/latest/release_check_report.json
```

Release checks should report the public exposure plan as passed, mark external
SSH staging as deferred for the chosen local-machine path, and keep launch
blocked by the remaining exposure, ops, release, and approval gates.

## Launch Gate

Feed the exposure report into the launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --local-machine-public-exposure-report .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json --release-check-report .eureka/release-checks/public-alpha/latest/release_check_report.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json
python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

The launch gate may record `external_staging_host_status=deferred`, but it must
not mark launch ready from a loopback exposure plan.

## Safety Posture

The plan keeps these disabled:

- public exposure;
- Workbench exposure;
- live metadata and public live fanout;
- mutation;
- downloads, file fetching, Wayback replay, extraction, install/emulation, and
  marketplace behavior;
- binary/download/execution/rights safety claims.

## Remaining Requirements

Before real public exposure, a future task must decide and validate:

- public exposure method;
- public base URL;
- TLS/domain posture;
- approved production auth or read-only no-auth posture;
- rate limiting;
- logging and privacy posture;
- monitoring;
- restart and rollback posture;
- operator approval evidence.

## Troubleshooting

- Missing local-machine staging report: rerun
  `python scripts/eureka_local_machine_staging.py smoke`.
- Invalid exposure plan: keep `public_exposure_enabled=false` and use
  `loopback_only` until a future exposure implementation task exists.
- External SSH staging still reported as missing: pass the exposure report to
  both release checks and the launch gate.
- Launch gate still blocked: expected until public exposure, TLS/domain,
  ops/auth posture, release checks, full discovery, and launch approval clear.
- Report leaks a path or token: regenerate after removing private values from
  optional plan inputs.

## Deferred

Public internet exposure from this computer, LAN exposure, tunnel setup,
reverse proxy setup, router port forwarding, production hosting, TLS/domain
setup, production auth implementation, public Workbench, public mutation,
public contribution intake, live IA indexing, public live source fanout,
downloads, file fetching, Wayback replay, extraction, install/emulation
behavior, marketplace behavior, release promotion, full discovery execution,
and public launch remain deferred.
