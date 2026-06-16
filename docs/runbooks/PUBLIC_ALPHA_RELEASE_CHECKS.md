# Public Alpha Release Checks

This runbook covers `PUBLIC-ALPHA-RELEASE-CHECKS-00`: a repeatable local
release-check gate over corpus closeout, staging, rehearsal, external staging,
and launch-gate reports.

It is not public launch, external staging apply, production hosting, TLS/domain
setup, production auth, release promotion, full discovery execution, or public
mutation.

## Clean Synced Checkpoint

Run release checks only from a clean, synced branch. If the external staging
configuration work is dirty, validate, commit, push, and verify `HEAD` matches
`origin/dev` first.

Useful preflight:

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/dev
```

Generated `.eureka` files are local ignored artifacts. Do not commit generated
release-check, launch-gate, staging, rehearsal, or external-staging outputs.

## Prerequisites

Validate the inputs that release checks consume:

```powershell
python scripts/eureka_public_alpha_corpus_gate.py validate --closeout .eureka/corpus-gate/public-alpha/latest

python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha

python scripts/eureka_public_alpha_rehearsal.py validate-report --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json

python scripts/eureka_external_staging.py validate-report --report .eureka/external-staging/public-alpha/latest/external_staging_report.json

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

Expected current posture:

```text
corpus_gate_status=pass
reviewed_artifact_gate_count=25
artifact_verified_count=25
binary_verified_count=0
download_safe_count=0
execution_safe_count=0
rights_cleared_count=0
local rehearsal GREEN
external staging dry-run or missing-config until an authorized host exists
launch_status BLOCKED until deployment, release, auth, and approval gates clear
```

## Run Release Checks

```powershell
python scripts/eureka_public_alpha_release_checks.py run --bundle .eureka/staging/public-alpha --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/release-checks/public-alpha/latest
```

If the current computer is being used as the loopback staging host, include the
local-machine staging report:

```powershell
python scripts/eureka_public_alpha_release_checks.py run --bundle .eureka/staging/public-alpha --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/release-checks/public-alpha/latest
```

See `docs/runbooks/LOCAL_MACHINE_STAGING_PROVISION.md`. Local-machine staging is
loopback evidence only; it does not clear external staging or production
hosting.

If the current computer is the chosen hosting path, generate and pass the
local-machine public exposure report:

```powershell
python scripts/eureka_public_alpha_release_checks.py run --bundle .eureka/staging/public-alpha --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --local-machine-public-exposure-report .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/release-checks/public-alpha/latest
```

See `docs/runbooks/LOCAL_MACHINE_PUBLIC_EXPOSURE_PLAN.md`. The exposure report
can defer the external SSH host path for local-machine hosting, but it keeps
public exposure disabled and launch blocked.

The command writes:

```text
.eureka/release-checks/public-alpha/latest/release_check_report.json
.eureka/release-checks/public-alpha/latest/RELEASE_CHECK_REPORT.md
```

By default it requires clean git, origin sync, generated-artifact cleanliness,
AIDE doctor/validate, architecture boundary checks, diff checks, corpus/staging
rehearsal/external/launch report validation, and the focused e2e lane for the
public-alpha release path.

For diagnostics only:

```powershell
python scripts/eureka_public_alpha_release_checks.py run ... --skip-tests --allow-dirty --no-require-origin-sync
```

Do not use diagnostic output as release readiness.

## Validate And Inspect

```powershell
python scripts/eureka_public_alpha_release_checks.py validate-report --report .eureka/release-checks/public-alpha/latest/release_check_report.json

python scripts/eureka_public_alpha_release_checks.py status --report .eureka/release-checks/public-alpha/latest/release_check_report.json
```

`PASS_WITH_WARNINGS` means local release/product checks passed, but public
release remains blocked. `local_release_checks_green` means the local corpus,
staging, rehearsal, external report consumption, focused tests, git posture, and
safety checks are green enough to identify the remaining launch blockers. It is
not public launch approval.

Use `--fail-on-blocked` when automation should return nonzero while release
blockers remain:

```powershell
python scripts/eureka_public_alpha_release_checks.py run --bundle .eureka/staging/public-alpha --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --launch-gate-report .eureka/launch/public-alpha/latest/launch_gate_report.json --out .eureka/release-checks/public-alpha/latest --fail-on-blocked
```

The nonzero exit is expected until blockers are cleared.

## Launch Gate Integration

Feed the release-check report back into the launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --external-staging-report .eureka/external-staging/public-alpha/latest/external_staging_report.json --local-machine-staging-report .eureka/local-machine-staging/public-alpha/latest/local_machine_staging_report.json --local-machine-public-exposure-report .eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json --release-check-report .eureka/release-checks/public-alpha/latest/release_check_report.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

The launch gate consumes:

```text
release_check_report_status
release_check_release_status
full_discovery_status
release_promotion_status
```

It must keep launch `BLOCKED` unless deployment, hosting, TLS/domain, auth or
approved no-auth posture, full discovery, release promotion, and approval are
actually satisfied.

## Full Discovery And Release Promotion

Release checks do not start full discovery and do not promote `dev` to a
release branch or `main`.

If future reports exist, pass them explicitly:

```powershell
python scripts/eureka_public_alpha_release_checks.py run ... --full-discovery-report path\to\full_discovery_report.json --release-promotion-report path\to\release_promotion_report.json
```

If the report status is absent, missing, unknown, or not run, the release-check
report keeps the release-process blocker open. A report cannot claim full
discovery or release promotion passed without report evidence.

## Safety Posture

Release checks must keep these disabled or absent:

- Workbench exposure;
- live metadata and public live fanout;
- public mutation;
- downloads, file fetching, Wayback replay, extraction, install/emulation, and
  marketplace behavior;
- binary/download/execution/rights safety claims.

The corpus gate currently verifies artifact identity metadata. It does not
claim binaries are safe, downloadable, executable, rights-cleared, or launch
ready.

## Expected Remaining Blockers

Until separately cleared, expect blockers for:

- external staging host and base URL;
- production hosting;
- TLS/domain;
- production auth or approved public read-only no-auth posture;
- full discovery and release promotion reports;
- public launch approval.

## Troubleshooting

- Dirty git tree: commit and push intended changes, or rerun with
  `--allow-dirty` only for diagnostics.
- `origin/dev` mismatch: pull/rebase or push until local `HEAD` equals
  `origin/dev`.
- Generated artifacts tracked: run
  `python scripts/check_generated_artifact_cleanliness.py --check --json` and
  remove tracked generated files.
- Failing focused tests: run the exact test command recorded in
  `command_results`.
- Invalid staging bundle: rerun `python scripts/eureka_staging.py validate`.
- Invalid rehearsal report: rerun rehearsal validate/report generation.
- Invalid external staging report: rerun external staging plan/deploy/smoke as
  appropriate.
- Missing full discovery report: expected until an operator/CI supplies one.
- Launch gate still blocked: inspect release, deployment, auth, and approval
  blockers; release checks do not override them.

## Deferred

External staging apply, production hosting, TLS/domain setup, production auth
implementation, public Workbench, public mutation, public contribution intake,
production review store, production index service, live IA indexing, public
live source fanout, downloads, file fetching, Wayback replay, extraction,
install/emulation behavior, marketplace behavior, release promotion, full
discovery execution unless explicitly supplied as evidence, and public launch
are deferred.
