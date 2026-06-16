# Public Alpha Rehearsal

This runbook covers `PUBLIC-ALPHA-REHEARSAL-00`: a repeatable local rehearsal
over a packaged public-alpha staging bundle. It is not an internet deployment,
production hosting setup, public launch approval, public mutation path, or
Workbench exposure.

## Build The Bundle

Create a local reviewed index and package it for public-alpha staging:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/eureka_review.py accept --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740" --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl --reviewer local_demo --reason "Public alpha rehearsal seed"

python scripts/eureka_index.py build --source local_demo --reviewed-records .eureka/local_reviewed_records.jsonl --out .eureka/local_search_index.reviewed.json

python scripts/eureka_public_alpha_corpus_gate.py closeout --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/corpus-gate/public-alpha/latest

python scripts/eureka_staging.py package --index .eureka/local_search_index.reviewed.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest --out .eureka/staging/public-alpha

python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha
```

Generated `.eureka` files are local artifacts. Do not commit them.
If the manual artifact gate is not yet 25/25, omit the corpus closeout step and
expect corpus blockers to remain.

## Run The Rehearsal

```powershell
python scripts/eureka_public_alpha_rehearsal.py run --bundle .eureka/staging/public-alpha --host 127.0.0.1 --port 8765 --out .eureka/rehearsals/public-alpha/latest
```

The command starts a loopback public-alpha server from the bundle, probes the
public routes, verifies Workbench routes are blocked, checks read-only posture,
checks for public response leakage, checks startup fail-closed conflicts, probes
a restart, and writes:

```text
.eureka/rehearsals/public-alpha/latest/rehearsal_report.json
.eureka/rehearsals/public-alpha/latest/REHEARSAL_REPORT.md
```

The expected local result is usually `PASS_WITH_WARNINGS`: the local rehearsal
passes, while real public launch blockers remain.

## Inspect And Validate The Report

```powershell
python scripts/eureka_public_alpha_rehearsal.py validate-report --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json

python scripts/eureka_public_alpha_rehearsal.py status --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json
```

After the rehearsal report is valid, run the launch-blocker closeout audit when
you need a machine-checkable launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --out .eureka/launch/public-alpha/latest
python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json
python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

See `docs/runbooks/PUBLIC_ALPHA_LAUNCH_BLOCKER_CLOSEOUT.md` for blocker
categories, `--fail-on-blocked`, and future evidence inputs.
See `docs/runbooks/PUBLIC_ALPHA_CORPUS_GATE_CLOSEOUT.md` for the public-safe
artifact identity export that makes staging and launch-gate corpus counts agree.
See `docs/runbooks/EXTERNAL_STAGING_HOST_PROVISION.md` for the next external
staging plan/package/config/dry-run path once local rehearsal remains green.
Configured external apply remains explicit and confirmation-gated.
See `docs/runbooks/LOCAL_MACHINE_STAGING_PROVISION.md` when the current
computer should be treated as the loopback staging host and reported separately
from external staging.
See `docs/runbooks/PUBLIC_ALPHA_RELEASE_CHECKS.md` for the release-check gate
that consumes the rehearsal, corpus, staging, external staging, and launch-gate
reports before any launch decision.

The JSON report includes:

- bundle id and digests;
- document, status, reviewed-record, and artifact-verified counts;
- routes probed and blocked routes probed;
- leakage checks;
- mutation checks;
- startup conflict checks for live metadata, Workbench, non-loopback host, and
  missing/unsafe bundles;
- search and record checks;
- restart/rollback notes;
- explicit launch blockers.

## Routes Probed

Public routes:

- `/`
- `/health`
- `/status`
- `/api/status`
- `/about`
- `/method`
- `/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- one returned `/record/{id}`
- `/record/__missing__`
- `/record/..%2F..%2Fprivate`

Blocked Workbench routes:

- `/workbench`
- `/workbench/api/status`
- `POST /workbench/api/review/accept`

## Safety Guarantees

The rehearsal checks that public-alpha remains:

- read-only;
- loopback-only for this local task;
- live metadata disabled;
- public live fanout disabled;
- Workbench disabled;
- downloads/file fetching/Wayback/install/emulation absent;
- free of local path, token, ledger, reviewed-record, and debug leakage in
  public responses;
- non-mutating for bundle files, local review artifacts, and local indexes.

Reviewed metadata/source leads remain `artifact_verified=false` unless a future
governed evidence path explicitly proves artifact verification.

## Rollback Or Restart

This task does not add production orchestration. For local rehearsal:

1. Keep the previous staging bundle directory.
2. Build and validate a new bundle in a separate directory.
3. Run the rehearsal against the new bundle.
4. Restart the local server with the chosen `--staging-bundle`.
5. To roll back, stop the server and restart it with the previous bundle path.

## Troubleshooting

- Missing bundle: run the build/package commands above.
- Invalid bundle: run `python scripts/eureka_staging.py validate --bundle ...`.
- Port in use: choose another loopback port or use `--port 0` in tests.
- Non-loopback refusal: use `127.0.0.1` or `localhost`; internet exposure is
  deferred.
- Live metadata conflict: public-alpha staging uses `metadata_fallback=none`.
- Workbench conflict: Workbench is not exposed in public-alpha rehearsal.
- Leakage failure: inspect route samples and remove local paths, tokens, or
  operator affordances from public responses.
- Mutation failure: rebuild the bundle from clean local artifacts and rerun the
  rehearsal.

## Deferred

External staging host, production hosting, TLS/domain, production auth, public
Workbench, public mutation, public contribution intake, official artifact gate
updates, verified artifact evidence promotion, production stores/services, live
IA indexing, public live fanout, downloads, file fetching, Wayback replay,
extraction, install/emulation behavior, marketplace behavior, detail route
systems beyond `/record/{id}`, deployment packaging, launch approval,
queue/current mutation, release promotion, and full discovery are deferred.
