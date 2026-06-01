# AIDE Latest Task Packet

## PHASE

REVIEW-LIVE-METADATA-CANDIDATES-00 - review live metadata candidates for possible local promotion

## GOAL

Review the 8 redacted Internet Archive metadata candidates from the bounded live metadata pilot and produce conservative promotion previews only where metadata evidence supports a limited reviewed metadata record or reviewed source lead.

## WHY

The public alpha remains reviewed-record poor. Live metadata produced real source-backed candidates, but metadata is evidence, not truth. This task creates review decisions and handoffs without claiming verified downloads, safety, rights clearance, or public launch readiness.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_alpha_reassess_01_result.json`
- `control/inventory/snapshot_refresh_01_result.json`
- `control/inventory/live_metadata_pilot_result.json`
- `examples/snapshots/refresh/live_metadata/live_metadata_candidate_section.json`

## CURRENT_STATE

- live metadata candidates reviewed: 8
- reviewed metadata record previews: 1
- reviewed source lead previews: 2
- useful leads: 1
- needs more evidence: 2
- duplicate/rejected decisions: 2
- public launch track: deferred for discovery coverage

## ALLOWED_PATHS

- `.aide/queue/REVIEW-LIVE-METADATA-CANDIDATES-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-02/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-02/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/review/**`
- `contracts/candidates/**`
- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/scout/**`
- `contracts/discovery/**`
- `contracts/source/action/**`
- `contracts/search/query_plan/**`
- `contracts/view/models/public_search/**`
- `contracts/projections/**`
- `contracts/local_apply/**`
- `runtime/review/live_metadata/**`
- `runtime/review/batch/**`
- `runtime/review/queue/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/candidates/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/scout/**`
- `runtime/discovery/**`
- `runtime/source/action/**`
- `runtime/local_apply/**`
- `runtime/local_eval/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/gateway/**`
- `runtime/public_alpha/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `surfaces/web/workbench/**`
- `surfaces/files/**`
- `surfaces/text/**`
- `surfaces/lite/**`
- `scripts/eureka_review_live_metadata_candidates.py`
- `scripts/eureka_live_metadata_review_report.py`
- `scripts/eureka_live_metadata_promotion_preview.py`
- `scripts/eureka_live_metadata_local_apply_handoff.py`
- `scripts/validate_review_live_metadata_candidates.py`
- `tests/runtime/test_review_live_metadata_candidates.py`
- `tests/runtime/test_live_metadata_evidence_sufficiency.py`
- `tests/runtime/test_live_metadata_review_decisions.py`
- `tests/runtime/test_live_metadata_promotion_preview.py`
- `tests/runtime/test_live_metadata_local_apply_handoff.py`
- `tests/runtime/test_live_metadata_snapshot_handoff.py`
- `tests/runtime/test_live_metadata_review_boundaries.py`
- `tests/operations/test_review_live_metadata_candidates_scripts.py`
- `tests/scripts/test_validate_review_live_metadata_candidates.py`
- `examples/review/live_metadata/**`
- `examples/candidates/live_metadata/**`
- `examples/live_metadata_pilot/**`
- `examples/snapshots/refresh/live_metadata/**`
- `examples/public_alpha/reassess/live_metadata/**`
- `examples/local_apply/live_metadata/**`
- `control/policies/review_live_metadata_candidates_policy.json`
- `control/policies/live_metadata_evidence_sufficiency_policy.json`
- `control/policies/live_metadata_promotion_preview_policy.json`
- `control/policies/live_metadata_review_non_claim_policy.json`
- `control/policies/live_metadata_local_apply_handoff_policy.json`
- `control/policies/live_metadata_snapshot_handoff_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/live_metadata_*review*.json`
- `control/inventory/live_metadata_candidate_review_matrix.json`
- `control/inventory/live_metadata_evidence_sufficiency_matrix.json`
- `control/inventory/live_metadata_promotion_preview_matrix.json`
- `control/inventory/live_metadata_local_apply_handoff_matrix.json`
- `control/inventory/live_metadata_snapshot_handoff_matrix.json`
- `control/inventory/live_metadata_public_alpha_reassess_handoff_matrix.json`
- `control/inventory/review_live_metadata_candidates_input_state.json`
- `docs/architecture/REVIEW_LIVE_METADATA_CANDIDATES.md`
- `docs/architecture/LIVE_METADATA_EVIDENCE_SUFFICIENCY.md`
- `docs/architecture/LIVE_METADATA_PROMOTION_PREVIEW.md`
- `docs/operations/REVIEW_LIVE_METADATA_CANDIDATES_RUNBOOK.md`
- `docs/operations/POST_REVIEW_LIVE_METADATA_PLAN.md`
- `docs/reference/LIVE_METADATA_REVIEW_DECISION.md`
- `docs/reference/REVIEWED_METADATA_RECORD.md`
- `docs/reference/REVIEWED_SOURCE_LEAD.md`
- `control/audits/review-live-metadata-candidates-00-v0/**`

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

## NON_GOALS

- No new live source calls.
- No deployment or publication.
- No public launch or production readiness claim.
- No download, extraction, execution, install, emulation, or model behavior.
- No reviewed, master, or public index mutation.
- No accepted truth creation.
- No verified download, malware-clean, or rights-clearance claim.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add live metadata review contracts, policies, runtime, CLIs, examples, inventory, audit pack, docs, and focused tests.
- Produce per-candidate evidence sufficiency, decisions, promotion previews, local apply handoff, snapshot refresh handoff, and public alpha reassess handoff.
- Keep all preview/application work separate from mutation gates.

## VALIDATION

- `git diff --check`
- `python scripts/validate_review_live_metadata_candidates.py`
- existing public alpha, snapshot refresh, live metadata pilot, review batch, SCOUT, candidate index, query planner, source validators
- focused live metadata review unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- 8 live metadata candidates reviewed.
- Preview counts are recorded from deterministic review output.
- No raw responses, live calls, downloads, extraction, model calls, mutation, accepted truth, malware-clean, rights-clearance, or public launch claim.
- Next recommended task is `SNAPSHOT-REFRESH-02`.

## OUTPUT_SCHEMA

Final report uses the user-requested LIVE_METADATA_REVIEW format with validation and boundary summaries.

## TOKEN_ESTIMATE

medium

## EVIDENCE

- `examples/review/live_metadata/`
- `control/inventory/live_metadata_review_result.json`
- `control/audits/review-live-metadata-candidates-00-v0/`
