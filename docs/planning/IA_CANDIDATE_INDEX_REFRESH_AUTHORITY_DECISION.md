# IA Candidate Index Refresh Authority Decision

Task: `IA-CANDIDATE-INDEX-REFRESH-AUTHORITY-00`

This document records the queue authority decision that unblocks the next
implementation task, `IA-CANDIDATE-INDEX-REFRESH-00`.

## Repo State

- branch: `dev`
- HEAD before authority changes: `99818b8fb5ac25f9bccba989e00115ef7af82393`
- origin/dev before authority changes: `99818b8fb5ac25f9bccba989e00115ef7af82393`
- origin/dev sync before authority changes: `0 0`
- worktree before authority changes: clean

## Queue Change

- previous recommended task: `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`
- new recommended task: `IA-CANDIDATE-INDEX-REFRESH-00`
- reason: the IA source-observation cache delta task has implementation and
  audit evidence, but repo-local queue authority had not yet been advanced.
- path blocker fixed: the task packet is created for the next task so the
  future implementation may touch only the narrow runtime, script, test, docs,
  audit, generated candidate-index, and optional contract paths it requires.

## Allowed Implementation Paths For Next Task

- `runtime/local/**`
- `scripts/eureka_candidate_index_refresh.py`
- `scripts/eureka_index.py` if the repo already uses it for local candidate index behavior
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/candidate-index/**`
- `contracts/source/**` only for a narrow source-observation/candidate bridge schema
- `contracts/index/**` only if an existing repo convention supports narrow index contracts

## Protected Paths

- `docs/canon/**`
- public exposure, tunnel, hosting, or launch code
- Workbench runtime unless separately authorized
- source/provider expansion beyond the existing IA source-observation cache delta
- reviewed/master index mutation paths
- public-index mutation paths
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
- evidence-ledger materialization remains forbidden
- no downloads, file fetches, Wayback replay, broad IA crawling, or provider
  network calls are authorized during candidate-index refresh
- no production-readiness or public-launch claim is made

## Validation

Final validation is recorded in
`control/audits/source_wave/ia_candidate_index_refresh_authority_v0/authority_decision.json`.

Recommended next task: `IA-CANDIDATE-INDEX-REFRESH-00`.
