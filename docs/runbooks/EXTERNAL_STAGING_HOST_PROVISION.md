# External Staging Host Provision

This runbook covers `EXTERNAL-STAGING-HOST-PROVISION-00` and
`EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG`: preparing, validating, and, when
explicitly configured and confirmed, transferring the public-alpha staging
bundle to an external staging host.

It is not public launch, production hosting, TLS/domain setup, production auth,
release promotion, or public mutation.

## Prerequisites

Start from the public-safe corpus gate and staging bundle:

```powershell
python scripts/eureka_public_alpha_corpus_gate.py status --closeout .eureka/corpus-gate/public-alpha/latest
python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha
python scripts/eureka_public_alpha_rehearsal.py validate-report --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json
```

Expected posture:

```text
corpus_gate_status=pass
artifact_verified_count=25
read_only=true
live_metadata_enabled=false
workbench_exposed=false
public_live_fanout=false
```

## External Staging Host Configuration

External staging reads configuration from a local ignored JSON file,
environment variables, or explicit CLI arguments. Do not commit credentials.

Create a redacted local template:

```powershell
python scripts/eureka_external_staging.py init-config --out .eureka/external-staging/public-alpha/latest/external_staging_config.local.example.json
```

Copy that template to the ignored local config path when a real staging host is
authorized:

```text
.eureka/external-staging/public-alpha/latest/external_staging_config.local.json
```

The local config shape is:

```json
{
  "config_schema_version": 1,
  "host": "",
  "user": "",
  "ssh_port": 22,
  "ssh_key_path": "",
  "remote_dir": "",
  "base_url": "",
  "service_port": 8765,
  "bind_host": "127.0.0.1",
  "exposure_approved": false,
  "deployment_mode": "ssh",
  "public_alpha_mode": true,
  "read_only": true,
  "live_metadata_enabled": false,
  "workbench_enabled": false,
  "public_live_fanout": false,
  "mutation_enabled": false,
  "downloads_enabled": false
}
```

Validate and inspect the local config without printing secrets:

```powershell
python scripts/eureka_external_staging.py validate-config --config .eureka/external-staging/public-alpha/latest/external_staging_config.local.json

python scripts/eureka_external_staging.py config-status --config .eureka/external-staging/public-alpha/latest/external_staging_config.local.json
```

If the local file is absent, both commands report `missing_config`. That is the
expected posture until an authorized host is available.

Supported environment variables:

```text
EUREKA_STAGING_HOST
EUREKA_STAGING_USER
EUREKA_STAGING_SSH_KEY
EUREKA_STAGING_SSH_PORT
EUREKA_STAGING_REMOTE_DIR
EUREKA_STAGING_BASE_URL
EUREKA_STAGING_SERVICE_PORT
EUREKA_STAGING_BIND_HOST
EUREKA_STAGING_EXPOSURE_APPROVED
```

Defaults are conservative:

```text
bind_host=127.0.0.1
service_port=8765
exposure_approved=false
```

Secrets are redacted from generated plans and reports. Private key contents are
never written to repo files or reports. The following fields must remain false:

```text
live_metadata_enabled
workbench_enabled
public_live_fanout
mutation_enabled
downloads_enabled
```

`bind_host=0.0.0.0` or any other non-loopback bind requires
`exposure_approved=true`. A non-local `base_url` also requires exposure
approval. This is still external staging, not production hosting or public
launch.

## Plan

```powershell
python scripts/eureka_external_staging.py plan --bundle .eureka/staging/public-alpha --config .eureka/external-staging/public-alpha/latest/external_staging_config.local.json --out .eureka/external-staging/public-alpha/latest

python scripts/eureka_external_staging.py validate-plan --plan .eureka/external-staging/public-alpha/latest/external_staging_plan.json
```

The plan records bundle identity, corpus gate posture, read-only safety flags,
and whether host, remote dir, base URL, and exposure approval are configured.

## Package

```powershell
python scripts/eureka_external_staging.py package --bundle .eureka/staging/public-alpha --plan .eureka/external-staging/public-alpha/latest/external_staging_plan.json --out .eureka/external-staging/public-alpha/latest/package
```

Package output includes:

```text
deployment_manifest.json
remote_run_command.txt
remote_smoke_commands.txt
rollback_instructions.txt
staging_bundle/
```

The package contains only the public-safe staging bundle. It excludes raw review
ledgers, raw reviewed records, Workbench tokens, live metadata config, secrets,
and mutation affordances.

## Dry Run

```powershell
python scripts/eureka_external_staging.py deploy --plan .eureka/external-staging/public-alpha/latest/external_staging_plan.json --dry-run
```

Dry run validates the plan and writes:

```text
.eureka/external-staging/public-alpha/latest/external_staging_report.json
.eureka/external-staging/public-alpha/latest/EXTERNAL_STAGING_REPORT.md
```

It does not connect to any host.

## Apply

Only run apply when an authorized host, user, remote dir, and deployment package
are configured. Apply requires explicit confirmation:

```powershell
python scripts/eureka_external_staging.py deploy --plan .eureka/external-staging/public-alpha/latest/external_staging_plan.json --apply --confirm-apply
```

Alternatively, set `EUREKA_STAGING_CONFIRM_APPLY=1` for the apply process.

Without confirmation, apply refuses before contacting any host and writes
`deployment_status=confirmation_required`.

If configuration is missing, apply refuses and writes a `PASS_WITH_WARNINGS`
report with `deployment_status=missing_config`.

The SSH/SCP apply path transfers only the generated public-safe package. It does
not install packages, start Workbench, enable live metadata, enable mutation, or
claim production deployment. If remote process management is still manual, the
report uses `deployment_status=transfer_complete_manual_start_required`; run
the generated `remote_run_command.txt` on the host before smoke.

## Smoke

```powershell
python scripts/eureka_external_staging.py smoke --plan .eureka/external-staging/public-alpha/latest/external_staging_plan.json
```

If `EUREKA_STAGING_BASE_URL` or `--base-url` is missing, smoke reports blocked
instead of faking route success.

When a reachable base URL is configured, smoke probes public read-only routes
and disabled Workbench routes. `/api/status` must report read-only public-alpha
posture, corpus gate pass, live metadata disabled, Workbench disabled, mutation
disabled, downloads disabled, and zero binary/download/execution/rights safety
counts.

## Validate And Inspect Report

```powershell
python scripts/eureka_external_staging.py validate-report --report .eureka/external-staging/public-alpha/latest/external_staging_report.json

python scripts/eureka_external_staging.py status --report .eureka/external-staging/public-alpha/latest/external_staging_report.json
```

`PASS_WITH_WARNINGS` is expected when no authorized host or base URL is
configured. That means the tooling, package, dry run, and reports are valid,
but external staging remains unprovisioned.

## Launch Gate

Feed the external staging report into the launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json
python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

The external staging blocker resolves only when the report shows an authorized
deployment or transfer-complete external staging state plus passing smoke
probes. Dry-run-only, missing-config, confirmation-required, blocked-smoke, or
manual-start-required-without-smoke reports keep the blocker open.

## Safety Guarantees

External staging must keep:

- Workbench disabled;
- live metadata disabled;
- public live fanout disabled;
- mutation disabled;
- downloads, file fetching, Wayback, install/emulation, and marketplace
  behavior disabled;
- public routes read-only.

## Rollback

Use the generated `rollback_instructions.txt` in the package. P0 rollback is a
manual operator action: stop the external staging process, restore the previous
`staging_bundle` directory, and restart the same read-only run command.

## Troubleshooting

- Missing config: create the local ignored config or set the
  `EUREKA_STAGING_*` environment variables. Until then, `PASS_WITH_WARNINGS`
  with `missing_config` is expected.
- Missing host: set `host`, `user`, and `remote_dir` in the local config, or
  set `EUREKA_STAGING_HOST`, `EUREKA_STAGING_USER`, and
  `EUREKA_STAGING_REMOTE_DIR`.
- Missing key: set `ssh_key_path` in the local ignored config or
  `EUREKA_STAGING_SSH_KEY` in local environment only. If system SSH auth is
  already configured, the key field may remain blank.
- Confirmation required: rerun apply with `--confirm-apply` only after checking
  the plan and package.
- Missing base URL: set `EUREKA_STAGING_BASE_URL` before smoke.
- Smoke blocked: expected when no base URL is configured.
- Smoke failed: inspect route probe results in `external_staging_report.json`.
- Port in use: change `EUREKA_STAGING_SERVICE_PORT`.
- Non-loopback refusal: set `exposure_approved=true` only for an approved
  staging exposure, and keep Workbench/live/mutation disabled.
- Workbench exposure: stop the server and restart without Workbench flags.
- Live metadata exposure: public-alpha staging must use metadata fallback `none`.
- Mutation exposure: restart the staging server in public-alpha read-only mode.
- Path/token leakage: rebuild staging and external package after removing the
  private field.
- Launch gate still blocked: expected until production hosting, TLS/domain,
  production auth/no-auth posture, release checks, and public approval are
  also cleared.

## Deferred

Production hosting, TLS/domain setup, production auth, public Workbench, public
mutation, public contribution intake, production review store, production index
service, live IA indexing, public live source fanout, downloads, file fetching,
Wayback replay, extraction, install/emulation behavior, marketplace behavior,
release promotion, full discovery execution, and public launch are deferred.
