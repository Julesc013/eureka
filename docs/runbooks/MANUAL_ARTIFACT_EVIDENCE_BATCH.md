# Manual Artifact Evidence Batch

This runbook covers `MANUAL-ARTIFACT-EVIDENCE-BATCH-01`: the first local
manual evidence batch workflow for Eureka public-alpha artifact gates.

It does not complete the 25-record gate by itself, launch public alpha, deploy
hosting, download binaries, fetch files, replay Wayback, or promote fixture/IA
metadata into verified artifact truth.

## Prerequisite Seed

Start from the reviewed-artifact gate seed bundle:

```powershell
python scripts/eureka_artifact_gate.py validate --gate .eureka/artifact-gate/public-alpha-seed

python scripts/eureka_artifact_gate.py status --gate .eureka/artifact-gate/public-alpha-seed
```

If the seed bundle is missing, rebuild the reviewed local index and rerun the
seed workflow in `docs/runbooks/REVIEWED_ARTIFACT_GATE_SEED.md`.

## Manual Batch Plan

```powershell
python scripts/eureka_artifact_gate.py manual-plan --gate .eureka/artifact-gate/public-alpha-seed --out .eureka/artifact-gate/manual-batch-01 --target-records 5
```

This writes:

```text
.eureka/artifact-gate/manual-batch-01/batch_manifest.json
.eureka/artifact-gate/manual-batch-01/candidate_plan.jsonl
```

The plan keeps excluded candidates visible. Broad queries such as `Windows 7
apps`, missing-hardware queries such as `driver for Win98`, unavailable records,
and fixture-only records without external evidence must not become verified
artifact records.

## Evidence Template

```powershell
python scripts/eureka_artifact_gate.py manual-template --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/manual_evidence_template.jsonl
```

Fill a separate `manual_evidence_packets.jsonl` from the template. Required
packet fields include:

- `evidence_packet_id`
- `batch_id`
- `candidate_id`
- `artifact_title`
- `artifact_type`
- `artifact_identity_fields`
- `platform_or_context`
- `source_observations`
- `evidence_urls` or `source_identifiers`
- `evidence_type`
- `source_authority`
- `observed_fields`
- `reviewer`
- `review_rationale`
- `collected_at` or `observed_at`
- `no_download_performed=true`
- `file_fetch_performed=false`
- `binary_verified=false`
- `download_safe=false`
- `execution_safe=false`
- `rights_cleared=false`
- `verification_scope`
- `artifact_verified`
- `gate_eligible`

Source observations should record page/catalog/release/support metadata only.
Do not download binaries, fetch files, crawl broadly, or replay Wayback.

## Acceptable Evidence

`artifact_verified=true` is allowed only when the packet has explicit reviewer
rationale and sufficient artifact identity evidence, such as:

- primary or official source metadata; or
- stable archive/catalog source plus independent reputable corroboration; or
- existing repo authority that explicitly treats the source type as sufficient.

`artifact_verified=true` does not mean:

- `binary_verified`
- `download_safe`
- `execution_safe`
- `rights_cleared`
- malware-safe

Those fields remain false unless a separate approved process proves them.

## Unacceptable Evidence

These may be useful source leads, but must not become verified artifact truth by
themselves:

- fixture-only records;
- IA metadata alone;
- local demo reviewed records;
- broad category queries;
- source hints without reviewer rationale;
- packet prep without external/source observation evidence.

Use `artifact_verified=false`, `gate_eligible=false`, and a clear
`gate_exclusion_reason` for insufficient packets.

## Ingest And Validate

When evidence packets are available:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/manual-batch-01/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01
```

If `manual_evidence_packets.jsonl` is absent, `manual-validate` reports a
blocked warning and fabricates no records.

Invalid packets are rejected. Common errors include missing reviewer, missing
rationale, missing source identity, fixture-only `artifact_verified=true`, and
insufficient verification scope.

To create manual evidence packets from bounded source observations, use
`docs/runbooks/ARTIFACT_EVIDENCE_SOURCE_COLLECTION.md`. Source collection
produces `manual_evidence_packets.jsonl` for this manual batch workflow; it
does not weaken the evidence criteria.

## Review And Report

```powershell
python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer manual_batch_01 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

The report writes:

```text
.eureka/artifact-gate/manual-batch-01/evidence_validation_report.json
.eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl
.eureka/artifact-gate/manual-batch-01/artifact_gate_report.json
.eureka/artifact-gate/manual-batch-01/ARTIFACT_GATE_REPORT.md
.eureka/artifact-gate/manual-batch-01/MANUAL_BATCH_REPORT.md
```

Expected current result without real evidence is `PASS_WITH_WARNINGS`,
`gate_status=blocked`, `artifact_verified_count=0`, and
`reviewed_artifact_gate_count=0/25`.

## Launch Gate

Feed the manual batch report into the public-alpha launch gate:

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

The launch gate can consume the manual batch report and remove unknown
artifact-gate authority. It must still remain blocked unless the artifact gate
target and all deployment, release, approval, and safety gates are truly clear.

## Troubleshooting

- No eligible candidates: inspect `candidate_plan.jsonl`; broad or
  under-specified records may need a narrower artifact identity.
- Missing evidence packets: fill `manual_evidence_packets.jsonl` from the
  template, or treat the batch as a source-collection handoff.
- Missing hardware details: do not verify Win98 driver records until vendor,
  model, chipset, or device identity is known.
- Invalid evidence packets: rerun `manual-validate` and fix reviewer,
  rationale, source identity, source authority, or verification scope.
- Inconsistent counts: rerun `manual-review`, then `manual-report`.
- Launch gate still blocked: expected until gate count, verified evidence,
  deployment, release, and approval blockers are resolved.

## Deferred

Completing the full 25-record artifact gate, official gate promotion, large
manual evidence expansion, live evidence harvesting as default behavior,
downloads, file fetching, Wayback replay, extraction, install/emulation,
marketplace behavior, external staging host provisioning, production hosting,
TLS/domain setup, production auth, public Workbench, public mutation, public
contribution intake, production stores/services, live IA indexing, public live
fanout, release promotion, full discovery execution, and public launch are
deferred.
