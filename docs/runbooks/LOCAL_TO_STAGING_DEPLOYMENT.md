# Local To Staging Deployment Rehearsal

This runbook covers `LOCAL-TO-STAGING-DEPLOYMENT-00`: a local staging
rehearsal for the read-only public-alpha surface. It is not an internet
deployment, production hosting path, public launch, public mutation path, or
public Workbench.

## Prerequisites

Build a reviewed local index:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/eureka_review.py accept --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740" --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl --reviewer local_demo --reason "Staging local reviewed seed"

python scripts/eureka_index.py build --source local_demo --reviewed-records .eureka/local_reviewed_records.jsonl --out .eureka/local_search_index.reviewed.json
```

## Package

Create the local staging bundle:

```powershell
python scripts/eureka_staging.py package --index .eureka/local_search_index.reviewed.json --out .eureka/staging/public-alpha
```

Generated layout:

```text
.eureka/staging/public-alpha/
  manifest.json
  public_search_index.json
  public_runtime_config.json
```

The bundle includes a sanitized public index derived from the reviewed local
index. It does not include the raw review ledger, raw reviewed-record JSONL,
Workbench tokens/config, live metadata config, secrets, absolute local paths,
or private generated artifacts.

After the manual artifact gate reaches 25/25, package the public-safe corpus
gate closeout into the bundle:

```powershell
python scripts/eureka_public_alpha_corpus_gate.py closeout --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/corpus-gate/public-alpha/latest

python scripts/eureka_staging.py package --index .eureka/local_search_index.reviewed.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest --out .eureka/staging/public-alpha
```

This adds public-safe artifact identity and evidence summary files to the
bundle. See `docs/runbooks/PUBLIC_ALPHA_CORPUS_GATE_CLOSEOUT.md`.

## Validate And Inspect

```powershell
python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha
python scripts/eureka_staging.py status --bundle .eureka/staging/public-alpha
```

Validation checks that the public index validates, manifest counts/digests
match, public-alpha/read-only posture is present, live metadata and Workbench
are disabled, mutation is disabled, and local paths/tokens/private artifacts
are not present.

## Smoke

```powershell
python scripts/eureka_staging.py smoke --bundle .eureka/staging/public-alpha --host 127.0.0.1 --port 8765
```

The smoke starts a local public-alpha server from the bundle, probes:

- `/`
- `/health`
- `/status`
- `/api/status`
- `/about`
- `/method`
- `/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- one returned `/record/{id}`
- `/workbench`
- `/workbench/api/status`

It verifies `read_only=true`, live metadata disabled, public live fanout
disabled, Workbench routes disabled, no local path/token leakage in public
responses, and no mutation of the bundle index.

## Public Alpha Rehearsal Report

After package/validate/smoke, run the repeatable rehearsal command when you need
a JSON and Markdown proof artifact:

```powershell
python scripts/eureka_public_alpha_rehearsal.py run --bundle .eureka/staging/public-alpha --host 127.0.0.1 --port 8765 --out .eureka/rehearsals/public-alpha/latest
python scripts/eureka_public_alpha_rehearsal.py validate-report --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json
python scripts/eureka_public_alpha_rehearsal.py status --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json
```

See `docs/runbooks/PUBLIC_ALPHA_REHEARSAL.md` for the route probes, mutation
checks, fail-closed checks, report fields, and explicit launch blockers.

If you want to use the current computer as the loopback staging host and emit a
separate local-machine staging report, see
`docs/runbooks/LOCAL_MACHINE_STAGING_PROVISION.md`. That path is not external
staging and does not expose the service to the internet.

If the current computer is also the chosen hosting path, use
`docs/runbooks/LOCAL_MACHINE_PUBLIC_EXPOSURE_PLAN.md` after local-machine
staging. That creates the no-exposure plan and launch-gate input before any
future tunnel, reverse proxy, LAN, or public-port task.

Then run the launch-blocker closeout audit when you need the machine-checkable
gate that separates local readiness from public launch readiness:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --out .eureka/launch/public-alpha/latest
```

See `docs/runbooks/PUBLIC_ALPHA_LAUNCH_BLOCKER_CLOSEOUT.md`.

To prepare a transfer package or dry-run an authorized external staging path,
see `docs/runbooks/EXTERNAL_STAGING_HOST_PROVISION.md`. External staging is
still not public launch or production hosting. Real apply requires a local
ignored config or environment configuration and explicit `--confirm-apply`.

## Run Server From Bundle

```powershell
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha
```

`--staging-bundle` validates the bundle, loads
`public_search_index.json`, forces public-alpha read-only posture, and reports
`deployment_source=staging_bundle` plus a public-safe `bundle_id` in
`/api/status`. It refuses live metadata, `--allow-live-metadata`,
`--enable-workbench`, and non-loopback hosts such as `0.0.0.0`.

Useful routes:

- `http://127.0.0.1:8765/`
- `http://127.0.0.1:8765/health`
- `http://127.0.0.1:8765/status`
- `http://127.0.0.1:8765/api/status`
- `http://127.0.0.1:8765/about`
- `http://127.0.0.1:8765/method`
- `http://127.0.0.1:8765/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `http://127.0.0.1:8765/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- a returned `/record/{id}` link

## Rollback And Restart

This task does not add production orchestration. Use bundle-path switching for
local rollback rehearsal:

1. Keep the previous bundle directory, for example `.eureka/staging/public-alpha-prev`.
2. Package a new bundle to a separate directory.
3. Validate and smoke the new bundle.
4. Restart `scripts/run_eureka_local.py` with the selected `--staging-bundle`.
5. To roll back, stop the server and restart it with the previous bundle path.

Generated staging bundles are ignored local artifacts. Do not commit them.

## Troubleshooting

- Missing index: rebuild `.eureka/local_search_index.reviewed.json` and rerun
  `package`.
- Invalid bundle: run `validate --bundle ...` and fix the reported missing
  file, digest, count, or posture error.
- Port in use: rerun smoke/server with another loopback port.
- Stale bundle: rebuild the reviewed index, repackage, validate, and smoke.
- Path leakage validation failure: inspect the reported bundle file and remove
  private review/index/source paths before repackaging.
- Workbench conflict: remove `--enable-workbench`; staging is public read-only.
- Live metadata conflict: use `--metadata-fallback none` and omit
  `--allow-live-metadata`.
- Non-loopback refusal: use `127.0.0.1` or `localhost`; external exposure is
  deferred.

## Deferred

Real internet deployment, staging machine provisioning, production hosting,
TLS/domain setup, production auth, public Workbench, public mutation, public
contribution intake, official artifact gate updates, verified artifact
promotion, production stores/services, live IA indexing, public live fanout,
downloads, file fetching, Wayback replay, extraction, install/emulation
behavior, marketplace behavior, detail route systems beyond `/record/{id}`,
queue/current mutation, and full discovery are deferred.
