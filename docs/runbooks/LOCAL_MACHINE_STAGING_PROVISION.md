# Local-Machine Staging Provision

This runbook covers `LOCAL-MACHINE-STAGING-PROVISION-00`: using the current
computer as a loopback staging host for the read-only public-alpha bundle.

It is not external SSH staging, public internet exposure, production hosting,
TLS/domain setup, release promotion, full discovery, or public launch.

## When To Use This

Use local-machine staging when you want the current computer to run the staged
public-alpha bundle and produce a machine-readable report:

```text
current computer -> public-alpha staging bundle -> loopback server -> route smoke -> local-machine staging report
```

This does not satisfy the external staging host blocker. It proves only that the
bundle can be hosted safely on `127.0.0.1`.

## Prerequisites

Create and validate the public-alpha staging bundle first:

```powershell
python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha
python scripts/eureka_staging.py status --bundle .eureka/staging/public-alpha
```

The expected bundle posture is:

```text
public_alpha_mode=true
read_only=true
corpus_gate_status=pass
reviewed_artifact_gate_count=25
artifact_verified_count=25
binary_verified_count=0
download_safe_count=0
execution_safe_count=0
rights_cleared_count=0
```

## Plan

```powershell
python scripts/eureka_local_machine_staging.py plan --bundle .eureka/staging/public-alpha --out .eureka/local-machine-staging/public-alpha/latest

python scripts/eureka_local_machine_staging.py validate-plan --plan .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_plan.json
```

The plan defaults to:

```text
host=127.0.0.1
port=8765
public_exposure=false
```

Non-loopback hosts such as `0.0.0.0` are rejected for this task.

## Smoke

```powershell
python scripts/eureka_local_machine_staging.py smoke --bundle .eureka/staging/public-alpha --host 127.0.0.1 --port 8765 --out .eureka/local-machine-staging/public-alpha/latest
```

The smoke starts a loopback public-alpha server from the bundle and probes:

- `/`
- `/health`
- `/status`
- `/api/status`
- `/about`
- `/method`
- `/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- one returned `/record/{id}`
- blocked Workbench routes and `POST /workbench/api/review/accept`

Expected safety posture:

- read-only true;
- Workbench disabled;
- live metadata disabled;
- public live fanout disabled;
- mutation disabled;
- downloads disabled;
- no unsafe binary/download/execution/rights claims.

## Validate And Inspect

```powershell
python scripts/eureka_local_machine_staging.py validate-report --report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json

python scripts/eureka_local_machine_staging.py status --report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json
```

The command writes:

```text
.eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json
.eureka/local-machine-staging/public-alpha/latest/LOCAL_MACHINE_STAGING_REPORT.md
```

Generated `.eureka` artifacts are local ignored files. Do not commit them.

## Release Checks

Pass the local-machine staging report to release checks as additional local
evidence:

```powershell
python scripts/eureka_public_alpha_release_checks.py run --bundle .eureka/staging/public-alpha --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/release-checks/public-alpha/latest

python scripts/eureka_public_alpha_release_checks.py validate-report --report .eureka/release-checks/public-alpha/latest/release_check_report.json
python scripts/eureka_public_alpha_release_checks.py status --report .eureka/release-checks/public-alpha/latest/release_check_report.json
```

Release checks should report local-machine staging as passed when the report is
valid. They must still keep external/public hosting blockers open unless a
future approved policy says local-machine hosting is an accepted substitute.

## Launch Gate

Pass the local-machine staging report to the launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --release-check-report .eureka/release-checks/public-alpha/latest/release_check_report.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json
python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

The launch gate may record `local_machine_staging_status=pass`, but it must not
mark launch ready from loopback hosting alone.

## Public Exposure Planning

After local-machine staging is green, use
`docs/runbooks/LOCAL_MACHINE_PUBLIC_EXPOSURE_PLAN.md` to record that the current
computer is the selected hosting path while public exposure remains disabled.
That report lets release checks and the launch gate defer the external SSH host
path without claiming public launch readiness.

## What Remains Blocked

Local-machine staging does not clear:

- public internet exposure;
- production hosting;
- TLS/domain setup;
- production auth or approved read-only no-auth posture;
- full discovery;
- release promotion;
- public launch approval.

## Troubleshooting

- Missing bundle: rerun staging package and validate.
- Invalid plan: confirm the host is `127.0.0.1` or another loopback address.
- Smoke route failure: run `python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha`.
- Workbench exposed: do not pass `--enable-workbench`; rebuild the staging bundle if unsafe config leaked.
- Live metadata enabled: public-alpha staging must use metadata fallback `none`.
- Mutation detected: inspect the bundle and local `.eureka` artifacts before rerunning.
- Launch gate still blocked: this is expected until hosting, TLS/domain, auth, release, and approval gates are cleared.

## Deferred

Public internet exposure from this computer, production hosting, TLS/domain
setup, production auth implementation, public Workbench, public mutation, public
contribution intake, live IA indexing, public live source fanout, downloads,
file fetching, Wayback replay, extraction, install/emulation behavior,
marketplace behavior, release promotion, full discovery execution, and public
launch remain deferred.
