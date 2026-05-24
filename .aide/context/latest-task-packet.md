# AIDE Latest Task Packet

## PHASE

WORKBENCH-LOCAL-LOOP-CLOSEOUT - AIDE-BATCH-WORKBENCH-LOCAL-LOOP-CLOSEOUT-01

## GOAL

Prove query to reviewed local result through the Local Apply Gate in temp scope.

## WHY

Close the first safe local product loop by composing the ResolutionRunKernel, Workbench projection, review/promote flow, Local Apply Gate, reviewed local index refresh, search-after-apply proof, and rollback proof without mutating the real operator instance.

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

- `.aide/**`
- `contracts/local_loop/**`
- `contracts/local_apply/**`
- `contracts/instances/**`
- `contracts/review/**`
- `contracts/candidates/**`
- `contracts/public_index/**`
- `contracts/resolution_run/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/local_loop/**`
- `runtime/local_apply/**`
- `runtime/instances/**`
- `runtime/public_index/**`
- `runtime/review_queue/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/evidence_ledger/**`
- `runtime/source_cache/**`
- `runtime/resolution_run/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/local_eval/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `surfaces/web/workbench/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `scripts/eureka_local_loop_closeout.py`
- `scripts/eureka_local_apply.py`
- `scripts/eureka_local_apply_backup.py`
- `scripts/eureka_local_apply_rollback.py`
- `scripts/eureka_workbench_review_promote.py`
- `scripts/eureka_workbench_live_run.py`
- `scripts/eureka_resolution_run.py`
- `scripts/validate_workbench_local_loop_closeout.py`
- `scripts/validate_local_apply_gate.py`
- `scripts/validate_workbench_review_promote.py`
- `scripts/validate_workbench_live_run.py`
- `scripts/validate_resolution_run_kernel.py`
- `scripts/eureka_test_select.py`
- `tools/generators/eureka_local_loop_closeout.py`
- `tools/validators/validate_workbench_local_loop_closeout.py`
- `tests/runtime/test_workbench_local_loop_closeout.py`
- `tests/runtime/test_local_loop_search_after_apply.py`
- `tests/runtime/test_local_loop_rollback.py`
- `tests/runtime/test_local_loop_boundaries.py`
- `tests/operations/test_workbench_local_loop_scripts.py`
- `tests/operations/test_workbench_local_loop_smoke.py`
- `tests/scripts/test_validate_workbench_local_loop_closeout.py`
- `examples/local_loop/**`
- `examples/local_apply/**`
- `examples/workbench/review_promote/**`
- `examples/reviewed_index_refresh/**`
- `examples/workbench/live_run/**`
- `examples/ia_live_metadata_lane/**`
- `examples/ia_hunt_bridge/**`
- `examples/workbench/result_lanes/**`
- `control/policies/workbench_local_loop_policy.json`
- `control/policies/workbench_local_loop_non_claim_policy.json`
- `control/policies/workbench_local_loop_boundary_policy.json`
- `control/policies/workbench_local_loop_operator_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/workbench_local_loop_*.json`
- `control/audits/workbench-local-loop-closeout-01-v0/**`
- `docs/operations/**`
- `docs/reference/**`
- `docs/architecture/WORKBENCH_LOCAL_LOOP.md`
- `docs/architecture/LOCAL_PRODUCT_LOOP.md`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `native/**`
- `crates/**`
- `evals/**`
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, and source AIDE repository state

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
- `py -3 .aide/scripts/aide_lite.py pack --task "AIDE-BATCH-WORKBENCH-LOCAL-LOOP-CLOSEOUT-01"`
- `python scripts/validate_workbench_local_loop_closeout.py`
- `python scripts/validate_local_apply_gate.py`
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

- No production/public launch claim.
- No public hosted behavior, public live source fanout, master-index mutation, committed public-index mutation, committed instance state, automatic candidate acceptance, review bypass, source probe, live IA call requirement, downloads/uploads, extraction, execution/install/emulation, model/provider calls, deployment, SOURCE-WAVE implementation, SNAPSHOT-RELAY implementation, native client implementation, or broad repo layout refactor.

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
- chars: 4806
- approx_tokens: 1202
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
