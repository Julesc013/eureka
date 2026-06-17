# IA Source Observation Cache Delta

This runbook covers `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`.

## What It Is

The IA source-observation cache delta is a local generated packet derived from
the completed IA metadata smoke report. It records source observations for a
bounded, approved smoke run so later source-index tasks can replay, audit, diff,
and validate what the source said.

The delta is source-observation-only. It is not reviewed truth.

## What It Is Not

- not public launch or public exposure
- not broad Archive.org crawling
- not a downloader
- not Wayback replay
- not a live public source fanout path
- not candidate-index materialization
- not evidence-ledger materialization
- not reviewed/master-index mutation
- not public-index mutation
- not rights clearance or malware/binary safety evidence

## Commands

Build:

```powershell
python scripts/eureka_source_observation_cache.py build-delta `
  --source ia_metadata `
  --smoke-report control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json `
  --out .eureka/source-wave/ia-metadata/source-observation-cache/latest
```

Validate:

```powershell
python scripts/eureka_source_observation_cache.py validate `
  --delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json `
  --strict
```

Status:

```powershell
python scripts/eureka_source_observation_cache.py status `
  --delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json
```

## Generated Artifacts

Generated local artifacts live under:

```text
.eureka/source-wave/ia-metadata/source-observation-cache/latest/
  source_observations.jsonl
  source_observation_delta_manifest.json
  SOURCE_OBSERVATION_CACHE_DELTA_REPORT.md
```

The `.eureka/` tree is local generated state and is ignored by git.

Tracked audit material lives under:

```text
control/audits/source_wave/ia_source_observation_cache_delta_v0/
```

## Safety Invariants

- no network or provider call during cache-delta build
- no downloads
- no file fetches
- no Wayback replay
- no public fanout
- no public mutation
- no candidate-index mutation
- no evidence-ledger mutation
- no reviewed/master mutation
- no public-index mutation
- review remains the truth boundary
- public exposure remains paused
- license posture remains restricted source-available

## Next Step

`IA-CANDIDATE-INDEX-REFRESH-00` may consume this source-observation cache delta
to create a candidate-index delta or dry-run. That next layer still must not
create reviewed/master truth.
