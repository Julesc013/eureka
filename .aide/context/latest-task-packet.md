# AIDE Latest Task Packet

## PHASE

REPO-MERGE-01 - Merge OBS side lane and Track B lane into unified main

## GOAL

Unify the preserved local Track B safety branch with the remote OBS side lane,
then update and push main normally if validation passes.

## WHY

REPO-SYNC-03 preserved a dirty merge-rescued worktree on the safety branch.
REPO-SYNC-04 confirmed that origin/main contained OBS-AGENT-01 through
OBS-AGENT-07 while the safety branch contained local Track B runtime and control
work. The current task intentionally merges the lanes while preserving safety
boundaries.

## CONTEXT_REFS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/repo-sync-03-active-merge-rescue-v0/`
- `control/audits/repo-sync-04-clean-convergence-audit-v0/`
- `control/audits/obs-agent-07-human-review-packet-v0/`
- `control/audits/track-b-23-integration-audit-v0/`
- `contracts/`
- `control/inventory/`
- `scripts/`
- `tests/`
- `docs/`
- `AGENTS.md`

## IMPLEMENTATION

- Merge origin/main into the preserved safety branch.
- Preserve OBS seed/review artifacts and local Track B runtime/control artifacts.
- Fix merged hardening wording without weakening forbidden-input detection.
- Refresh stale public-alpha rehearsal evidence using its generator.
- Add REPO-MERGE-01 audit evidence.
- Update local main from the unified branch and push normally if validation passes.

## VALIDATION

- `git status --short`
- `git diff --check`
- precise conflict-marker scan
- `python scripts/check_architecture_boundaries.py`
- OBS validators
- Track B validators
- `python -m unittest discover -s tests -t .`
- AIDE Lite doctor, validate, test, selftest, verify, eval, review-pack, and adapter checks

## EVIDENCE

- `control/audits/repo-merge-01-unified-main-v0/README.md`
- `control/audits/repo-merge-01-unified-main-v0/repo_merge_01_report.json`
- `control/audits/repo-merge-01-unified-main-v0/merge_conflict_resolution.md`
- `control/audits/repo-merge-01-unified-main-v0/merged_commit_inventory.md`
- `control/audits/repo-merge-01-unified-main-v0/validation.md`
- `control/audits/repo-merge-01-unified-main-v0/push_result.md`
- `control/audits/repo-merge-01-unified-main-v0/next_steps.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/audits/repo-merge-01-unified-main-v0/README.md`
- `control/audits/repo-merge-01-unified-main-v0/repo_merge_01_report.json`
- `control/audits/repo-merge-01-unified-main-v0/merge_conflict_resolution.md`
- `control/audits/repo-merge-01-unified-main-v0/merged_commit_inventory.md`
- `control/audits/repo-merge-01-unified-main-v0/validation.md`
- `control/audits/repo-merge-01-unified-main-v0/push_result.md`
- `control/audits/repo-merge-01-unified-main-v0/next_steps.md`
- `control/audits/repo-merge-01-unified-main-v0/stale_aide_resolution.md`
- `control/audits/repo-merge-01-unified-main-v0/obs_track_b_unified_state.md`
- `control/audits/repo-merge-01-unified-main-v0/post_merge_validator_matrix.md`
- `docs/operations/public_alpha_rehearsal_evidence_v0/COMMIT_AND_ARTIFACTS.md`
- `docs/operations/public_alpha_rehearsal_evidence_v0/README.md`
- `docs/operations/public_alpha_rehearsal_evidence_v0/SIGNOFF_TEMPLATE.md`
- `docs/operations/public_alpha_rehearsal_evidence_v0/rehearsal_evidence_manifest.json`
- `scripts/build_observation_candidate_review_queue.py`
- `scripts/generate_source_gap_observation_candidates.py`
- `scripts/validate_obs_agent_local_eval_mining.py`
- `scripts/validate_obs_human_review_packet.py`
- `scripts/validate_obs_track_b_synchronization.py`
- `scripts/validate_observation_candidate_review_queue.py`
- `scripts/validate_search_need_seed_candidates.py`
- `scripts/validate_source_gap_observation_candidates.py`
- `scripts/validate_workunit_seed_candidates.py`

## FORBIDDEN_PATHS

- environment files
- secret or credential directories
- ignored local AIDE/private-state roots
- ignored cache roots
- destructive Git history edits
- branch deletion
- force push
- master-index mutation
- public-index mutation
- source access approval
- WorkUnit execution
- live source, network, browser, provider, upload, download, account, or telemetry activation

## NON_GOALS

- Do not force push.
- Do not delete branches.
- Do not rebase or rewrite history.
- Do not approve source access.
- Do not execute WorkUnits.
- Do not create public truth.
- Do not mutate the public index or master index.
- Do not enable live source, connector, hosted, upload, download, account, telemetry, browser, model, or provider behavior.

## ACCEPTANCE

- OBS-AGENT-01 through OBS-AGENT-07 artifacts remain present.
- Local Track B artifacts remain present.
- No conflict markers remain.
- Targeted validators pass.
- Full unittest suite passes.
- AIDE checks have zero errors, with documented WARN-only findings allowed.
- Local main is updated to the unified branch.
- Main is pushed normally without force.

## OUTPUT_SCHEMA

Final response reports status, summary, commits, branches, merge result,
validation, push result, risks, and next task.

## TOKEN_ESTIMATE

- latest task packet: under 2400 tokens
- latest review packet: under 2400 tokens

## NEXT_REVIEW_GATE

- HUMAN-OBS-REVIEW-01 - Review OBS candidate packet.
- Continue Track B from the next task after the latest merged Track B state, without enabling live source behavior.
