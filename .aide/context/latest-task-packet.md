# AIDE Latest Task Packet

## PHASE

LIVE-METADATA-PILOT-BATCH-00 - operator-approved live metadata pilot over seed
queries

## GOAL

Prepare and gate a bounded live metadata pilot over frontier-media and
legacy-software seed queries. Dry-run and fixture modes are implemented now.
Approved live metadata calls remain blocked until an operator approval file is
present.

## WHY

The public alpha remains reviewed-record thin. Eureka needs real source-backed
candidates, but live metadata observations must stay metadata-only,
redacted, review-gated, and non-mutating.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_alpha_reassess_result.json`
- `control/inventory/snapshot_refresh_result.json`
- `control/inventory/seed_batch_frontier_media_result.json`
- `control/inventory/seed_batch_legacy_software_result.json`
- `control/inventory/public_search_ux_model_result.json`

## ALLOWED_PATHS

- `.aide/queue/LIVE-METADATA-PILOT-BATCH-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-01/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/source/action/live_metadata_pilot_*.json`
- `runtime/seed_batches/live_metadata_pilot.py`
- `runtime/seed_batches/__init__.py`
- `scripts/eureka_live_metadata_pilot_*.py`
- `scripts/validate_live_metadata_pilot_batch.py`
- `tests/runtime/test_live_metadata_pilot_*.py`
- `tests/operations/test_live_metadata_pilot_batch_scripts.py`
- `tests/scripts/test_validate_live_metadata_pilot_batch.py`
- `examples/live_metadata_pilot/**`
- `examples/candidates/live_metadata/**`
- `examples/scout/live_metadata/**`
- `examples/review_batch/live_metadata/**`
- `examples/snapshots/refresh/live_metadata/**`
- `examples/public_alpha/reassess/live_metadata/**`
- `control/policies/live_metadata_pilot_*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/live_metadata_pilot*.json`
- `control/audits/live-metadata-pilot-batch-00-v0/**`
- `docs/architecture/LIVE_METADATA_PILOT_BATCH.md`
- `docs/operations/LIVE_METADATA_PILOT_BATCH_RUNBOOK.md`
- `docs/operations/LIVE_METADATA_PILOT_APPROVAL.md`
- `docs/operations/POST_LIVE_METADATA_PILOT_PLAN.md`
- `docs/reference/LIVE_METADATA_PILOT_RESULT.md`
- `docs/reference/LIVE_METADATA_REDACTION_POLICY.md`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens
- provider credentials
- raw live source responses
- raw IA responses
- raw full-discovery stdout/stderr logs
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Add approval template and approval validation.
- Add dry-run and fixture pilot modes.
- Select at least four frontier-media and four legacy-software seed queries.
- Build metadata-only Internet Archive request plans.
- Redact transport summaries before candidate normalization.
- Normalize fixture/redacted summaries into review-only CandidateRecords.
- Build SCOUT, ReviewBatch, SnapshotRefresh, and PublicAlphaReassess handoffs.
- Stop at `WAITING_FOR_OPERATOR_LIVE_METADATA_APPROVAL` if approval is absent.

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

## COMMITS

Use repo-policy-compliant equivalent of:

```text
policy(source): prepare live metadata pilot approval
```

## EVIDENCE

- `control/inventory/live_metadata_pilot_result.json`
- `control/inventory/live_metadata_pilot_batch_approval_state.json`
- `control/audits/live-metadata-pilot-batch-00-v0/`
- `examples/live_metadata_pilot/approval_template.json`

## NON_GOALS

- No live metadata calls without approval.
- No deployment, publish, or launch/readiness claim.
- No public live source fanout or public mutation.
- No downloads, extraction, installs, execution, or model/provider calls.
- No raw live response commit.
- No reviewed/master/public index mutation.
- No accepted truth creation.

## ACCEPTANCE

- Approval template exists.
- Dry-run request plans build.
- Fixture mode produces review-only candidate handoffs.
- Validator and focused tests pass.
- If approval is absent, final status is
  `WAITING_FOR_OPERATOR_LIVE_METADATA_APPROVAL`.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `REQUIRED_APPROVAL`, `VALIDATION`, `BOUNDARIES`,
and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1450
- budget_status: PASS
