# AIDE Latest Task Packet

## PHASE

IA-LIVE-METADATA-LANE-01

## GOAL

Add an explicit operator-approved live Internet Archive metadata lane for local resolution runs.

## WHY

Continue AIDE token survival by using repo-local context refs, compact objectives, deterministic validation, and evidence packets instead of long chat history.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/repo-snapshot.json` (present)
- `.aide/context/repo-map.json` (present)
- `.aide/context/repo-map.md` (present)
- `.aide/context/test-map.json` (present)
- `.aide/context/context-index.json` (present)
- `.aide/context/latest-context-packet.md` (present)
- `.aide/repo/latest-repo-intelligence.md` (present)
- `.aide/repo/file-inventory.json` (present)
- `.aide/reports/file-quality-summary.md` (present)
- `.aide/reports/file-quality-ledger.json` (present)
- `.aide/refactors/latest-refactor-readiness.md` (present)
- `.aide/refactors/latest-refactor-plan.example.json` (present)
- `.aide/routing/latest-route-decision.json` (present)
- `.aide/routing/latest-route-decision.md` (present)
- `.aide/cache/latest-cache-keys.json` (present)
- `.aide/cache/latest-cache-keys.md` (present)
- `.aide/prompts/compact-task.md`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/local-state.yaml`

## ALLOWED_PATHS

- `.aide/queue/AIDE-BATCH-IA-LIVE-METADATA-LANE-01/**`
- `.aide/queue/IA-LIVE-METADATA-LANE-01/**`
- `.aide/queue/WORKBENCH-REVIEW-PROMOTE-01/**`
- `.aide/queue/LOCAL-APPLY-GATE-01/**`
- `.aide/queue/SOURCE-WAVE-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/resolution_run/**`
- `contracts/search_interaction/**`
- `contracts/sources/**`
- `contracts/source_cache/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/resolution_run/**`
- `runtime/source_observation/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/review_queue/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/local_eval/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `surfaces/web/workbench/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `scripts/eureka_resolution_run.py`
- `scripts/eureka_workbench_live_run.py`
- `scripts/eureka_ia_live_metadata_lane.py`
- `scripts/eureka_ia_hunt_bridge.py`
- `scripts/validate_ia_live_metadata_lane.py`
- `scripts/validate_workbench_live_run.py`
- `scripts/validate_resolution_run_kernel.py`
- `scripts/validate_ia_hunt_bridge.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_ia_live_metadata_lane.py`
- `tests/runtime/test_ia_live_metadata_lane_policy.py`
- `tests/runtime/test_ia_live_metadata_lane_events.py`
- `tests/runtime/test_ia_live_metadata_lane_projection.py`
- `tests/runtime/test_ia_live_metadata_lane_boundaries.py`
- `tests/operations/test_ia_live_metadata_lane_scripts.py`
- `tests/operations/test_ia_live_metadata_lane_smoke.py`
- `tests/scripts/test_validate_ia_live_metadata_lane.py`
- `examples/ia_live_metadata_lane/**`
- `examples/workbench/live_run/**`
- `examples/resolution_run/**`
- `examples/ia_hunt_bridge/**`
- `examples/workbench/result_lanes/**`
- `control/policies/ia_live_metadata_lane_policy.json`
- `control/policies/ia_live_metadata_lane_operator_policy.json`
- `control/policies/ia_live_metadata_lane_rate_limit_policy.json`
- `control/policies/ia_live_metadata_lane_redaction_policy.json`
- `control/policies/ia_live_metadata_lane_non_claim_policy.json`
- `control/inventory/ia_live_metadata_lane_input_state.json`
- `control/inventory/ia_live_metadata_lane_route_matrix.json`
- `control/inventory/ia_live_metadata_lane_command_matrix.json`
- `control/inventory/ia_live_metadata_lane_event_matrix.json`
- `control/inventory/ia_live_metadata_lane_policy_matrix.json`
- `control/inventory/ia_live_metadata_lane_result_lane_matrix.json`
- `control/inventory/ia_live_metadata_lane_boundary_report.json`
- `control/inventory/ia_live_metadata_lane_live_smoke_result.json`
- `control/inventory/ia_live_metadata_lane_validation_matrix.json`
- `control/inventory/ia_live_metadata_lane_result.json`
- `control/inventory/ia_live_metadata_lane_next_task_decision.json`
- `control/inventory/ia_live_metadata_lane_failure_repair_log.json`
- `docs/architecture/IA_LIVE_METADATA_LANE.md`
- `docs/architecture/LIVE_SOURCE_ACTION_POLICY.md`
- `docs/operations/IA_LIVE_METADATA_LANE_RUNBOOK.md`
- `docs/operations/POST_IA_LIVE_METADATA_LANE_PLAN.md`
- `docs/reference/IA_LIVE_METADATA_LANE_EVENTS.md`
- `docs/reference/IA_LIVE_METADATA_LANE_COMMANDS.md`
- `control/audits/ia-live-metadata-lane-01-v0/**`

## FORBIDDEN_PATHS

- `.git/**`
- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens
- committed provider credentials
- raw prompts
- raw responses
- raw live IA response bodies
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py snapshot`
- `py -3 .aide/scripts/aide_lite.py index`
- `py -3 .aide/scripts/aide_lite.py context`
- `py -3 .aide/scripts/aide_lite.py pack --task "AIDE-EVAL-GREEN-01"`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest discover -s tests -t .`
- `git diff --check`

## COMMITS

- Commit coherent subdeliverables with verbose bodies.
- Stop at review gates.

## EVIDENCE

- changed files
- validation commands and results
- verifier result
- review packet path and result when review-pack is available
- advisory route decision path and result when Q17 routing is available
- compact packet size and budget status
- unresolved risks and deferrals

## NON_GOALS

- No live IA calls by default.
- No public live IA fanout.
- No downloads/uploads, IA file fetch, extraction, execution/install/emulation, model/provider calls, or deployment.
- No operator instance mutation by default and no committed instance state.
- No reviewed-index, master-index, or public-index mutation.
- No raw live IA response body commits.
- No production readiness, public launch readiness, marketplace/app-store readiness, or full Archive.org integration claim.
- No additional source-family implementation or broad crawler.

## ACCEPTANCE

- Task-specific acceptance criteria are met.
- Validation is run and recorded.
- Evidence is written.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4790
- approx_tokens: 1198
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
