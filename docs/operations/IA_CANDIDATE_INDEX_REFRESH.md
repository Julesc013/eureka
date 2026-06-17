# IA Candidate Index Refresh

This runbook covers `IA-CANDIDATE-INDEX-REFRESH-00`.

## What It Is

The IA candidate-index refresh consumes the governed IA source-observation
cache delta and writes a local generated candidate-index delta. The candidates
are provisional, unreviewed, and source-observation-backed so later tasks can
audit, diff, validate, and prepare review material.

The delta is candidate-only. It is not accepted truth.

## What It Is Not

- not public launch or public exposure
- not broad Archive.org crawling
- not a downloader
- not Wayback replay
- not a live public source fanout path
- not reviewed/master-index mutation
- not public-index mutation
- not evidence-ledger materialization
- not review or promotion
- not rights clearance or malware/binary safety evidence

## Commands

Build:

```powershell
python scripts/eureka_candidate_index_refresh.py build-delta `
  --source ia_metadata `
  --source-observation-delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json `
  --out .eureka/source-wave/ia-metadata/candidate-index/latest
```

Validate:

```powershell
python scripts/eureka_candidate_index_refresh.py validate `
  --delta .eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json `
  --strict
```

Status:

```powershell
python scripts/eureka_candidate_index_refresh.py status `
  --delta .eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json
```

## Generated Artifacts

Generated local artifacts live under:

```text
.eureka/source-wave/ia-metadata/candidate-index/latest/
  candidate_index_delta.jsonl
  candidate_index_delta_manifest.json
  CANDIDATE_INDEX_REFRESH_REPORT.md
```

The `.eureka/` tree is local generated state and is ignored by git.

Tracked audit material lives under:

```text
control/audits/source_wave/ia_candidate_index_refresh_v0/
```

## Safety Invariants

- no network or provider call during candidate-index refresh
- no downloads
- no file fetches
- no Wayback replay
- no public fanout
- no public mutation
- no evidence-ledger mutation
- no reviewed/master mutation
- no public-index mutation
- no review or promotion
- candidates remain provisional and unreviewed
- source-observation refs are preserved
- review remains the truth boundary
- public exposure remains paused
- license posture remains restricted source-available

## Inputs And Outputs

This refresh consumes `IA-SOURCE-OBSERVATION-CACHE-DELTA-00` output from:

```text
.eureka/source-wave/ia-metadata/source-observation-cache/latest/
```

It feeds `IA-EVIDENCE-LEDGER-SUMMARY-00`, which may summarize source
observations and candidate refs as evidence support. That next layer still must
not create reviewed/master truth or public-index mutation.
