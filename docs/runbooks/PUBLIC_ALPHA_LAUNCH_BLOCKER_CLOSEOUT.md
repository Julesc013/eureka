# Public Alpha Launch Blocker Closeout

This runbook covers `PUBLIC-ALPHA-LAUNCH-BLOCKER-CLOSEOUT-00`: a repeatable
local launch-gate audit over a packaged staging bundle and public-alpha
rehearsal report. It is not a deployment, public launch, release promotion,
verified evidence promotion, or production readiness claim.

## Prerequisites

Build and validate the local public-alpha staging bundle:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/eureka_review.py accept --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740" --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl --reviewer local_demo --reason "Public alpha rehearsal seed"

python scripts/eureka_index.py build --source local_demo --reviewed-records .eureka/local_reviewed_records.jsonl --out .eureka/local_search_index.reviewed.json

python scripts/eureka_public_alpha_corpus_gate.py closeout --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/corpus-gate/public-alpha/latest

python scripts/eureka_staging.py package --index .eureka/local_search_index.reviewed.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest --out .eureka/staging/public-alpha

python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha
```

If the corpus gate is not yet 25/25, omit the corpus closeout command and
expect corpus/evidence blockers to remain.

Run and validate the local rehearsal:

```powershell
python scripts/eureka_public_alpha_rehearsal.py run --bundle .eureka/staging/public-alpha --host 127.0.0.1 --port 8765 --out .eureka/rehearsals/public-alpha/latest

python scripts/eureka_public_alpha_rehearsal.py validate-report --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json
```

Generated `.eureka` files are local ignored artifacts. Do not commit them.

## Audit

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --out .eureka/launch/public-alpha/latest
```

The audit reads the staging bundle and rehearsal report, checks public-alpha
safety posture, classifies unresolved launch blockers, and writes:

```text
.eureka/launch/public-alpha/latest/launch_gate_report.json
.eureka/launch/public-alpha/latest/LAUNCH_GATE_REPORT.md
```

Expected current status is `PASS_WITH_WARNINGS` with
`launch_status=BLOCKED`: local rehearsal is green, but public launch gates are
not cleared.

## Validate And Inspect

```powershell
python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

`status` prints local rehearsal state, launch status, blocker count, blocker
categories, the next recommended task, and the report path.

## Enforce Blocked Mode

Use `--fail-on-blocked` when automation should fail while launch blockers
remain:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --out .eureka/launch/public-alpha/latest --fail-on-blocked
```

This command should exit nonzero while the current launch blockers remain. That
nonzero exit is expected and does not mean the audit tool failed.

## Blocker Categories

The report groups blockers into:

- `local_rehearsal_blockers`
- `safety_blockers`
- `corpus_evidence_blockers`
- `deployment_blockers`
- `release_process_blockers`
- `approval_blockers`
- `unknown_authority_blockers`

Current blockers without a supplied artifact gate report and corpus closeout
include missing official artifact gate evidence, missing verified artifact
evidence promotion, `artifact_verified_count=0`, missing external staging host,
missing production hosting, missing TLS/domain, missing production auth or
approved no-auth posture, missing full discovery/release promotion checks, and
missing public launch approval. After `SOURCE-OBSERVATION-BATCH-09`, use
`docs/runbooks/PUBLIC_ALPHA_CORPUS_GATE_CLOSEOUT.md` to create the public-safe
closeout and rebuild staging. That resolves the corpus count/staging mismatch
blockers, but launch still remains blocked until deployment, release-process,
auth, and approval blockers are cleared.

Local demo reviewed records do not satisfy the official reviewed-artifact gate.
Fixture, fallback, live metadata, and rehearsal outputs are not verified
artifact evidence.

## Supplying Future Evidence

The audit can reflect future evidence without requiring it now:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit `
  --bundle .eureka/staging/public-alpha `
  --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json `
  --out .eureka/launch/public-alpha/latest `
  --artifact-gate-report path\to\artifact_gate_report.json `
  --verified-evidence-report path\to\verified_evidence_report.json `
  --full-discovery-report path\to\full_discovery_report.json `
  --release-check-report path\to\release_check_report.json `
  --approval-file path\to\approval.json `
  --external-staging-url https://staging.example.invalid `
  --public-url https://example.invalid `
  --production-auth-posture approved
```

The command reads provided files locally. It does not perform external network
checks, deploy services, promote evidence, update gate counts, or approve a
launch.

For the local reviewed-artifact gate seed workflow, see
`docs/runbooks/REVIEWED_ARTIFACT_GATE_SEED.md`. Its generated
`artifact_gate_report.json` can be supplied with `--artifact-gate-report`; the
report is still blocker evidence, not verified artifact promotion.

For filled manual evidence batches, see
`docs/runbooks/MANUAL_ARTIFACT_EVIDENCE_BATCH.md`. Manual batch reports can
also be supplied with `--artifact-gate-report`; launch remains blocked unless
the gate target and all other launch blockers are actually cleared.

For bounded source observation packets that feed manual evidence batches, see
`docs/runbooks/ARTIFACT_EVIDENCE_SOURCE_COLLECTION.md`. Source collection
reports are operational evidence; the launch gate should consume the resulting
manual batch artifact gate report, not treat source leads as public launch
approval. `SOURCE-OBSERVATION-BATCH-09` is the first expected local batch that
can close the reviewed-artifact count at `25/25`; it is still not a public
launch approval.

For packaging the 25/25 artifact identity metadata into the public-alpha
staging/rehearsal path, see
`docs/runbooks/PUBLIC_ALPHA_CORPUS_GATE_CLOSEOUT.md`.

For the external staging blocker, see
`docs/runbooks/EXTERNAL_STAGING_HOST_PROVISION.md`. A dry-run report keeps the
blocker open; only an authorized deployment plus passing external smoke probes
can resolve it. Configured apply requires an ignored local config or
environment configuration and explicit confirmation; missing config should be
reported as a blocker, not silently downgraded.

If the current computer is being used as the loopback staging host, see
`docs/runbooks/LOCAL_MACHINE_STAGING_PROVISION.md` and pass
`--local-machine-staging-report`. A passing local-machine report is useful
operational evidence, but it does not satisfy external staging, production
hosting, TLS/domain, production auth, release promotion, or launch approval.

For the local release-check lane that consumes corpus closeout, staging,
rehearsal, external staging, and launch-gate reports, see
`docs/runbooks/PUBLIC_ALPHA_RELEASE_CHECKS.md`. Supplying its
`release_check_report.json` lets the launch gate distinguish green local
release checks from unresolved public launch blockers.

## Local Readiness Vs Launch Readiness

Local readiness means the staging bundle and rehearsal passed local read-only
safety checks.

Public launch readiness requires separate evidence for corpus/artifact gates,
verified evidence promotion, deployment/hosting/TLS, production auth or an
approved no-auth posture, release promotion checks, and public launch approval.

The launch gate must not report `READY` while any required blocker is unresolved
or unknown.

## Troubleshooting

- Invalid bundle: run `python scripts/eureka_staging.py validate --bundle ...`.
- Invalid rehearsal report: run `python scripts/eureka_public_alpha_rehearsal.py validate-report --report ...`.
- Unknown gate source: pass the relevant report path, or leave the blocker
  explicitly unknown.
- `--fail-on-blocked` exits nonzero: inspect the blocker categories; this is
  expected until gates are cleared.
- Stale generated reports: rerun staging package, rehearsal, then launch gate
  audit.
- Path/token leakage: inspect the source bundle or rehearsal output and remove
  private paths, tokens, or operator affordances before rerunning.

## Deferred

External staging host provisioning, production hosting, TLS/domain setup,
production auth implementation, public Workbench, public mutation, public
contribution intake, official artifact gate updates, verified artifact evidence
promotion, official/public gate promotion beyond the local generated Batch 09
manual report, production review store, production index service, live IA
indexing, public live fanout, downloads, file fetching, Wayback replay,
extraction, install/emulation behavior, marketplace behavior, rich UI redesign,
detail route systems beyond `/record/{id}`, queue/current mutation, full
discovery execution, release promotion, and actual public launch are deferred.
