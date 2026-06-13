# Reviewed Artifact Gate Seed

This runbook covers `REVIEWED-ARTIFACT-GATE-SEED-00`: a local, generated
artifact-gate seed workflow for public-alpha launch readiness. It prepares
candidate lists, manual evidence templates, non-verified seed records, and an
artifact gate report.

It does not verify artifacts, fetch files, download binaries, replay Wayback
captures, promote evidence, update official gate counts, or approve public
launch.

## Prerequisites

Build a local reviewed index:

```powershell
python scripts/eureka_index.py build --source local_demo --out .eureka/local_search_index.json

python scripts/eureka_review.py accept --index .eureka/local_search_index.json --query "manual for Sound Blaster CT1740" --ledger .eureka/local_review_ledger.jsonl --records .eureka/local_reviewed_records.jsonl --reviewer local_demo --reason "Artifact gate local source lead seed"

python scripts/eureka_index.py build --source local_demo --reviewed-records .eureka/local_reviewed_records.jsonl --out .eureka/local_search_index.reviewed.json
```

Generated `.eureka` files are local ignored artifacts. Do not commit them.

## Candidate List

```powershell
python scripts/eureka_artifact_gate.py candidates --index .eureka/local_search_index.reviewed.json --out .eureka/artifact-gate/public-alpha-seed/candidates.jsonl
```

The candidate list is deterministic and includes:

- specific artifact/source-lead candidates that can seed manual evidence work;
- broad or under-specified records marked excluded;
- source/evidence hints and provenance;
- `artifact_verified=false` and `gate_eligible=false`.

For example, broad `Windows 7 apps` and under-specified `driver for Win98`
records are excluded until they become specific artifact identities.

## Evidence Template

```powershell
python scripts/eureka_artifact_gate.py evidence-template --candidates .eureka/artifact-gate/public-alpha-seed/candidates.jsonl --out .eureka/artifact-gate/public-alpha-seed/evidence_template.jsonl
```

The template is for manual completion. Required review fields such as reviewer,
rationale, source identity, and verification scope must be filled before any
future evidence can be considered.

Fixture-only, IA-metadata-only, and local reviewed source-lead records are not
artifact verification.

## Seed Bundle

```powershell
python scripts/eureka_artifact_gate.py seed --index .eureka/local_search_index.reviewed.json --out .eureka/artifact-gate/public-alpha-seed --max-records 5
```

The seed command writes:

```text
.eureka/artifact-gate/public-alpha-seed/candidates.jsonl
.eureka/artifact-gate/public-alpha-seed/evidence_template.jsonl
.eureka/artifact-gate/public-alpha-seed/evidence_packets.jsonl
.eureka/artifact-gate/public-alpha-seed/reviewed_artifact_records.jsonl
.eureka/artifact-gate/public-alpha-seed/artifact_gate_report.json
.eureka/artifact-gate/public-alpha-seed/ARTIFACT_GATE_REPORT.md
```

The generated evidence packets and reviewed artifact records are source leads
only. They keep:

```text
artifact_verified=false
gate_eligible=false
binary_verified=false
download_safe=false
execution_safe=false
```

## Validate And Inspect

```powershell
python scripts/eureka_artifact_gate.py validate --gate .eureka/artifact-gate/public-alpha-seed

python scripts/eureka_artifact_gate.py status --gate .eureka/artifact-gate/public-alpha-seed
```

Expected current status is `PASS_WITH_WARNINGS` with `gate_status=blocked`.
The artifact gate count remains `0/25` until real, reviewed artifact evidence
exists.

Validate a manually edited evidence packet or JSONL file:

```powershell
python scripts/eureka_artifact_gate.py validate-evidence --evidence .eureka/artifact-gate/public-alpha-seed/evidence_packets.jsonl
```

Validation rejects:

- missing reviewer or rationale;
- missing source identity;
- fixture-only verified claims;
- `artifact_verified=true` without adequate verification scope;
- any download, file-fetch, binary verification, download-safety, or
  execution-safety claim created by this seed workflow.

## Launch Gate Integration

Export the seed report for the launch gate:

```powershell
python scripts/eureka_artifact_gate.py export-launch-report --gate .eureka/artifact-gate/public-alpha-seed --out .eureka/artifact-gate/public-alpha-seed/artifact_gate_report.json
```

Then pass it into the public-alpha launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/public-alpha-seed/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

This removes ambiguity about the artifact-gate seed report being present, but
it does not clear the launch gate. The launch gate remains blocked while the
official reviewed-artifact count is below target and verified artifact evidence
is absent.

To continue into filled manual evidence packets, use
`docs/runbooks/MANUAL_ARTIFACT_EVIDENCE_BATCH.md`.

## Safety Guarantees

This workflow:

- reads local indexes and generated local evidence files;
- writes only generated `.eureka/artifact-gate/...` outputs;
- creates no verified artifact truth;
- performs no live network access;
- performs no downloads, file fetches, Wayback replay, extraction, install, or
  emulation;
- does not mutate public indexes, master indexes, canon, release files,
  queue/current, official reviewed records, or gate counts.

## Troubleshooting

- Missing index: build `.eureka/local_search_index.reviewed.json` first.
- No candidates: rebuild the local reviewed index and inspect candidate output.
- Broad or under-specified records excluded: narrow the artifact identity before
  manual evidence work.
- Evidence validation fails: fill reviewer, rationale, source identity, and
  keep `artifact_verified=false` unless a future reviewed process proves the
  artifact.
- Launch gate still blocked: expected until manual evidence, official gate
  counts, deployment, release, and approval blockers are cleared.
- Stale seed report: rerun `seed`, `validate`, then launch-gate audit.

## Deferred

Manual evidence collection, artifact evidence promotion, official gate count
updates, 25-reviewed-record gate completion, live IA evidence, downloads, file
fetching, Wayback replay, extraction, install/emulation behavior, production
review store, production index service, Workbench evidence UI, public mutation,
release promotion, external staging/prod hosting, TLS/domain setup, public
approval, queue/current mutation, full discovery execution, and public launch
are deferred.
