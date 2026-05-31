# AIDE Latest Task Packet

## PHASE

LIVE-METADATA-PILOT-BATCH-00-CONTINUE - approved bounded Archive.org metadata
pilot

## GOAL

Run the approved bounded Internet Archive metadata pilot over selected
frontier-media and legacy-software seed queries, then commit only redacted
candidate/review/snapshot/reassessment evidence.

## WHY

The public alpha remains reviewed-record thin. Eureka needs real source-backed
candidates, but live metadata observations must stay metadata-only, redacted,
review-gated, and non-mutating.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/approvals/live-metadata-pilot-batch-00-approval.json`
- `control/inventory/live_metadata_pilot_result.json`
- `control/inventory/public_alpha_reassess_result.json`
- `control/inventory/snapshot_refresh_result.json`
- `control/inventory/public_search_ux_model_result.json`

## CURRENT_STATE

- Approval verified: true
- Source family: internet_archive_metadata
- Selected queries: 8
- Total live metadata requests: 16
- Candidate summaries created: true
- Candidate index handoff created: true
- SCOUT trails created: true
- Review batch packet created: true
- Snapshot refresh handoff created: true
- Public alpha reassess input created: true

## ALLOWED_PATHS

- `.aide/queue/LIVE-METADATA-PILOT-BATCH-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-01/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/approvals`
- `control/approvals/**`
- `control/approvals/live-metadata-pilot-batch-00-approval.json`
- `runtime/seed_batches/live_metadata_pilot.py`
- `scripts/validate_live_metadata_pilot_batch.py`
- `examples/live_metadata_pilot/**`
- `examples/candidates/live_metadata/**`
- `examples/scout/live_metadata/**`
- `examples/review_batch/live_metadata/**`
- `examples/snapshots/refresh/live_metadata/**`
- `examples/public_alpha/reassess/live_metadata/**`
- `control/inventory/live_metadata_pilot*.json`
- `control/audits/live-metadata-pilot-batch-00-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
- `secrets/**`
- `.env`
- raw live source responses
- raw IA responses
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Validate the operator approval phrase and boundary acknowledgements.
- Run dry-run request planning before live metadata.
- Run one approved live Internet Archive metadata pilot within the request cap.
- Commit redacted transport summaries, candidate summaries, review handoffs,
  snapshot handoffs, public alpha reassess input, and boundary evidence.
- Keep fixture examples deterministic and separate from live redacted evidence.

## VALIDATION

- `git diff --check`
- `python scripts/validate_live_metadata_pilot_batch.py`
- `python scripts/validate_public_search_ux_model.py`
- `python scripts/validate_public_alpha_reassess.py`
- `python scripts/validate_snapshot_refresh.py`
- `python scripts/validate_seed_batch_legacy_software.py`
- `python scripts/validate_seed_batch_frontier_media.py`
- `python scripts/validate_review_batch.py`
- `python scripts/validate_scout_runtime.py`
- `python scripts/validate_candidate_index_runtime.py`
- `python scripts/validate_query_to_source_action_planner.py`
- `python scripts/validate_source_action_kernel.py`
- `python scripts/validate_source_wave.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- focused live metadata pilot unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit
  check when practical

Full unittest discovery is not run by policy.

## EVIDENCE

- `control/inventory/live_metadata_pilot_result.json`
- `control/inventory/live_metadata_pilot_transport_summary.json`
- `control/inventory/live_metadata_pilot_redaction_summary.json`
- `control/inventory/live_metadata_pilot_candidate_matrix.json`
- `control/inventory/live_metadata_pilot_review_matrix.json`
- `control/inventory/live_metadata_pilot_snapshot_handoff_matrix.json`
- `control/audits/live-metadata-pilot-batch-00-v0/`
- `examples/live_metadata_pilot/redacted_metadata_summary.json`

## NON_GOALS

- No deployment, publish, or launch/readiness claim.
- No public live source fanout or public mutation.
- No downloads, extraction, installs, execution, or model/provider calls.
- No raw live response commit.
- No reviewed/master/public index mutation.
- No accepted truth creation.

## ACCEPTANCE

- Approval is verified.
- Live metadata request count is within the 24-request budget.
- Candidate summaries and handoffs are created from redacted metadata summaries.
- Boundary flags remain false.
- Next recommended task is `SNAPSHOT-REFRESH-01`.

## OUTPUT_SCHEMA

Return `STATUS`, `LIVE_METADATA_PILOT`, `VALIDATION`, `BOUNDARIES`, and
`NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1320
- budget_status: PASS
