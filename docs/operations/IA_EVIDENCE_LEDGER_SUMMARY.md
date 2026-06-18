# IA Evidence Ledger Summary

This runbook covers `IA-EVIDENCE-LEDGER-SUMMARY-00`.

## What It Is

The IA evidence-ledger summary consumes the governed IA source-observation
cache delta and provisional candidate-index delta, then writes a local generated
evidence-summary delta. The summaries preserve source observation refs,
candidate refs, query refs, provider modes, conservative support posture, and
review state.

The delta is evidence-summary-only. It is review material, not accepted truth.

## What It Is Not

- not public launch or public exposure
- not broad Archive.org crawling
- not a provider or network task
- not a downloader
- not Wayback replay
- not reviewed/master-index mutation
- not public-index mutation
- not candidate-index store mutation
- not authoritative evidence-ledger store mutation
- not review, promotion, or accepted-truth creation
- not rights clearance or malware/binary/download safety evidence

## Evidence Summary Types

Supported evidence-summary types are conservative source-supported clues:

- title/name clue
- date/time clue
- platform clue
- object-type clue
- representation/member clue
- source-location clue
- provenance clue
- absence clue
- near-miss clue
- conflicting-metadata clue
- transport/unavailability clue
- other typed source-supported clue

The implementation must not invent a clue when source-observation or candidate
fields do not provide supporting material.

## Support Postures

Allowed support postures are:

- `supports_clue`
- `metadata_mention`
- `candidate_support`
- `conflicting`
- `insufficient`
- `source_unavailable`
- `unknown`

Do not use `verified`, `accepted`, `authoritative`, `proven`, `safe`, or
`rights_cleared` except inside explicit negative or non-claim fields.

## Commands

Build:

```powershell
python scripts/eureka_evidence_ledger_summary.py build-delta `
  --source ia_metadata `
  --source-observation-delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json `
  --candidate-index-delta .eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json `
  --out .eureka/source-wave/ia-metadata/evidence-ledger/latest
```

Validate:

```powershell
python scripts/eureka_evidence_ledger_summary.py validate `
  --delta .eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json `
  --strict
```

Status:

```powershell
python scripts/eureka_evidence_ledger_summary.py status `
  --delta .eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json
```

## Generated Artifacts

Generated local artifacts live under:

```text
.eureka/source-wave/ia-metadata/evidence-ledger/latest/
  evidence_summaries.jsonl
  evidence_summary_delta_manifest.json
  EVIDENCE_LEDGER_SUMMARY_REPORT.md
```

The `.eureka/` tree is local generated state and is ignored by git.

Tracked audit material lives under:

```text
control/audits/source_wave/ia_evidence_ledger_summary_v0/
```

## Safety Invariants

- no network or provider call during evidence-summary generation
- no downloads
- no file fetches
- no Wayback replay
- no public fanout
- no public mutation
- no reviewed/master mutation
- no public-index mutation
- no candidate-index store mutation
- no evidence-ledger store mutation
- no review or promotion
- no accepted truth creation
- evidence summaries remain provisional and unreviewed
- source and candidate refs are preserved
- review remains the truth boundary
- public exposure remains paused
- license posture remains restricted source-available

## Inputs And Outputs

This task consumes:

```text
.eureka/source-wave/ia-metadata/source-observation-cache/latest/
.eureka/source-wave/ia-metadata/candidate-index/latest/
```

It feeds `REVIEW-IA-CANDIDATES-BATCH-00`, where a human review task may inspect
the summaries and candidates. Review still gates truth; this runbook does not
authorize reviewed/master or public-index mutation.
