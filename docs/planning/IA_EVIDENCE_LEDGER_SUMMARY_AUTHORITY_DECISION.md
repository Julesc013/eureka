# IA Evidence Ledger Summary Authority Decision

Task: `IA-EVIDENCE-LEDGER-SUMMARY-AUTHORITY-00`

This document records the queue authority decision that unblocks the next
implementation task, `IA-EVIDENCE-LEDGER-SUMMARY-00`.

## Repo State

- branch: `dev`
- HEAD before authority changes: `9a597fc2498172143b0a05c32f09cc4aeeaf9c27`
- origin/dev before authority changes: `9a597fc2498172143b0a05c32f09cc4aeeaf9c27`
- origin/dev sync before authority changes: `0 0`
- worktree before authority changes: clean

## Queue Change

- previous recommended task: `IA-CANDIDATE-INDEX-REFRESH-00`
- new recommended task: `IA-EVIDENCE-LEDGER-SUMMARY-00`
- reason: the IA candidate-index refresh task has implementation and audit
  evidence, but repo-local queue authority had not yet been advanced.
- path blocker fixed: the task packet is created for the next task so the
  future implementation may touch only the narrow runtime, script, test, docs,
  audit, generated evidence-ledger, and optional contract paths it requires.

## Allowed Implementation Paths For Next Task

- `runtime/local/**`
- `scripts/eureka_evidence_ledger_summary.py`
- `scripts/eureka_index.py` if the repo already uses it for local source-index summaries
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/evidence-ledger/**`
- `contracts/source/**` only for a narrow source/candidate/evidence bridge schema
- `contracts/evidence/**` only if an existing repo convention supports narrow evidence contracts

## Protected Paths

- `docs/canon/**`
- public exposure, tunnel, hosting, or launch code
- Workbench runtime unless separately authorized
- source/provider expansion beyond the existing IA source-observation and candidate deltas
- reviewed/master index mutation paths
- public-index mutation paths
- candidate-index store mutation paths
- review/promotion mutation paths
- `release/**`
- `archive/**`
- existing archive zips
- `LICENSE.md`
- `LICENSE-SUMMARY.md`
- `NOTICE.md`
- `.aide/queue/**` except final status reporting if repo convention requires it

## Safety Decision

- public exposure remains paused
- license posture remains restricted source-available and unchanged
- reviewed/master mutation remains forbidden
- public-index mutation remains forbidden
- candidate-index store mutation remains forbidden
- review/promotion remains forbidden
- no downloads, file fetches, Wayback replay, broad IA crawling, or provider
  network calls are authorized during evidence-ledger summary
- evidence summary output remains support material, not reviewed truth
- no production-readiness or public-launch claim is made

## Validation

Final validation is recorded in
`control/audits/source_wave/ia_evidence_ledger_summary_authority_v0/authority_decision.json`.

Recommended next task: `IA-EVIDENCE-LEDGER-SUMMARY-00`.
