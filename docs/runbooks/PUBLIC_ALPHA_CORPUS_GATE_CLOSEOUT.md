# Public Alpha Corpus Gate Closeout

This runbook covers `PUBLIC-ALPHA-CORPUS-GATE-CLOSEOUT-00`: turning a passed
manual artifact gate report into public-safe corpus artifacts for the local
public-alpha staging and launch-gate path.

It does not launch public alpha, deploy hosting, promote canon or release
state, fetch files, download binaries, replay Wayback, approve public mutation,
or claim binary/download/execution/rights safety.

## Prerequisite Gate Status

Confirm the manual artifact gate is actually closed:

```powershell
python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Expected gate-close state after `SOURCE-OBSERVATION-BATCH-09`:

```text
reviewed_artifact_gate_count=25
artifact_verified_count=25
gate_status=PASS
```

Here `artifact_verified=true` means artifact identity metadata is verified. It
does not mean `binary_verified`, `download_safe`, `execution_safe`,
`rights_cleared`, malware-safe, or launch-ready.

## Close Out The Corpus Gate

```powershell
python scripts/eureka_public_alpha_corpus_gate.py closeout --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/corpus-gate/public-alpha/latest

python scripts/eureka_public_alpha_corpus_gate.py validate --closeout .eureka/corpus-gate/public-alpha/latest

python scripts/eureka_public_alpha_corpus_gate.py status --closeout .eureka/corpus-gate/public-alpha/latest
```

The closeout writes generated local artifacts:

```text
.eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json
.eureka/corpus-gate/public-alpha/latest/CORPUS_GATE_CLOSEOUT.md
.eureka/corpus-gate/public-alpha/latest/public_artifact_identity_records.jsonl
.eureka/corpus-gate/public-alpha/latest/public_artifact_evidence_summary.jsonl
```

Generated `.eureka` files are local ignored artifacts. Do not commit them.

## Public-Safe Export

`public_artifact_identity_records.jsonl` contains one public-safe identity
record per unique counted artifact. Each record preserves artifact identity
metadata, evidence refs, source authority summary, and the no-download posture.

The export must not include absolute local paths, `.eureka` paths, tokens,
Workbench affordances, mutation actions, download/install/emulation actions, or
long copyrighted excerpts.

`public_artifact_evidence_summary.jsonl` contains concise evidence summaries
for those identities. It summarizes observed source fields and limitations
rather than copying large source text.

## Package Staging With Corpus Closeout

```powershell
python scripts/eureka_staging.py package --index .eureka/local_search_index.reviewed.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest --out .eureka/staging/public-alpha

python scripts/eureka_staging.py validate --bundle .eureka/staging/public-alpha

python scripts/eureka_staging.py status --bundle .eureka/staging/public-alpha
```

The staging bundle includes the public-safe corpus artifacts and reports:

```text
corpus_gate_status=pass
reviewed_artifact_gate_count=25
artifact_verified_count=25
binary_verified_count=0
download_safe_count=0
execution_safe_count=0
rights_cleared_count=0
```

The public search index may still have
`public_search_index_artifact_verified_count=0` because indexed local demo
search records are separate from the public corpus gate export.

## Rehearse Public Alpha

```powershell
python scripts/eureka_public_alpha_rehearsal.py run --bundle .eureka/staging/public-alpha --host 127.0.0.1 --port 8765 --out .eureka/rehearsals/public-alpha/latest

python scripts/eureka_public_alpha_rehearsal.py validate-report --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json

python scripts/eureka_public_alpha_rehearsal.py status --report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json
```

The local rehearsal should remain green or `PASS_WITH_WARNINGS` only for
remaining launch blockers. Public status should show corpus gate pass and the
identity-metadata-only safety posture.

## Audit The Launch Gate

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

Expected result:

- corpus/evidence count blocker resolved;
- staging bundle `artifact_verified_count` no longer `0`;
- launch remains `BLOCKED` by non-corpus gates such as external staging host,
  production hosting, TLS/domain, production auth or approved no-auth posture,
  full discovery/release promotion checks, and public launch approval.

## Troubleshooting

- Count below 25: rerun manual batch review/report/status and fix evidence
  packets before closeout.
- Duplicate artifact identity: inspect `dedupe_identity_key` and do not count
  the duplicate.
- Local path or token leakage: remove the private value from public-facing
  source fields and rerun closeout.
- Binary safety claim leakage: keep `binary_verified`, `download_safe`,
  `execution_safe`, and `rights_cleared` false unless a separate approved
  process proves them.
- Inconsistent staging manifest: rerun corpus closeout, package, validate, and
  status in that order.
- Launch gate still blocked: expected unless deployment, release, auth, and
  approval gates are also cleared.

## Deferred

Release promotion, canon promotion, deployment, external staging host
provisioning, production hosting, TLS/domain setup, production auth, public
Workbench, public mutation, public contribution intake, production review
store, production index service, live IA indexing, public live source fanout,
downloads, file fetching, Wayback replay, extraction, install/emulation
behavior, marketplace behavior, full discovery execution, and public launch are
deferred.
