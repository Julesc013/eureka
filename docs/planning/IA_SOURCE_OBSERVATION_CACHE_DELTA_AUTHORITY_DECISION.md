# IA Source Observation Cache Delta Authority Decision

Task: `IA-SOURCE-OBSERVATION-CACHE-DELTA-AUTHORITY-00`

This document records the queue authority decision that unblocks the next
implementation task, `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`.

## Repo State

- branch: `dev`
- HEAD before authority changes: `1860ffaa5099ce5eeebac592d7cfa544a5aa5a9e`
- origin/dev before authority changes: `1860ffaa5099ce5eeebac592d7cfa544a5aa5a9e`
- origin/dev sync before authority changes: `0 0`
- worktree before authority changes: clean

## Queue Change

- previous recommended task: `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`
- new recommended task: `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`
- reason: the IA metadata smoke task has implementation and audit evidence, but
  repo-local queue authority had not yet been advanced.
- path blocker fixed: the generated task packet is refreshed for the next task
  so the future implementation may touch the narrow runtime, script, test,
  docs, audit, generated delta, and optional contract paths that it requires.

## Allowed Implementation Paths For Next Task

- `runtime/local/**`
- `scripts/eureka_source_observation_cache.py`
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/source-observation-cache/**`
- `contracts/source/**` only for a narrow source-observation cache schema

## Protected Paths

- `docs/canon/**`
- public exposure, tunnel, hosting, or launch code
- Workbench runtime unless separately authorized
- source/provider expansion beyond the IA metadata smoke path
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
- no downloads, file fetches, Wayback replay, or broad IA crawling are authorized
- no live provider calls are authorized during cache-delta build
- no production-readiness or public-launch claim is made

## Validation

Final validation is recorded in
`control/audits/source_wave/ia_source_observation_cache_delta_authority_v0/authority_decision.json`.

Recommended next task: `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`.
