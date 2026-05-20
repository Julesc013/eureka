# AIDE Latest Task Packet

## PHASE

AIDE-BATCH-IA-HUNT-WORKBENCH-01 - IA-HUNT-BRIDGE-00

## GOAL

Implement the local IA metadata to Hunt, WorkUnit, and Workbench result-lane bridge.

## WHY

Connect the existing IA metadata pilot pieces to Search Hunt, IA WorkUnits, temp-instance proof writes, and Workbench result-lane projections without live IA calls, source probes, downloads, extraction, model/provider calls, deployment, operator-instance mutation, or production/public launch claims.

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
- `AGENTS.md`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/source_observation/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/review_queue/**`
- `runtime/public_index/**`
- `runtime/local_workbench/**`
- `runtime/local_service/**`
- `runtime/local_eval/**`
- `surfaces/web/workbench/**`
- `surfaces/api/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `contracts/workunits/**`
- `contracts/sources/**`
- `contracts/source_cache/**`
- `contracts/evidence/**`
- `contracts/candidates/**`
- `contracts/review/**`
- `scripts/eureka_ia_hunt_bridge.py`
- `scripts/eureka_workbench_result_lanes.py`
- `scripts/validate_ia_hunt_bridge.py`
- `scripts/validate_workbench_result_lanes.py`
- `scripts/validate_search_interaction_contract.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_ia_hunt_bridge.py`
- `tests/runtime/test_ia_hunt_workunits.py`
- `tests/runtime/test_ia_hunt_result_lanes.py`
- `tests/runtime/test_workbench_result_lanes.py`
- `tests/operations/test_ia_hunt_bridge_scripts.py`
- `tests/operations/test_ia_hunt_bridge_smoke.py`
- `tests/scripts/test_validate_ia_hunt_bridge.py`
- `examples/ia_hunt_bridge/**`
- `examples/workbench/result_lanes/**`
- `docs/operations/**`
- `docs/architecture/IA_HUNT_BRIDGE.md`
- `docs/reference/**`
- `control/inventory/**`
- `control/audits/**`
- `control/policies/**`
- `scripts/local_queue_progress.py`
- `scripts/validate_*.py`
- `scripts/check_*.py`
- `tests/operations/**`
- `tests/aide/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `site/**`
- `native/**`
- `crates/**`
- `evals/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `data/public_index/**`
- `instances/**`
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, and source AIDE repository state

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Implement the bridge as an orchestrator over existing IA metadata pieces.
- Preserve generated/manual boundaries and temp-instance-only write posture.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py snapshot`
- `py -3 .aide/scripts/aide_lite.py index`
- `py -3 .aide/scripts/aide_lite.py context`
- `py -3 .aide/scripts/aide_lite.py pack --task "IA-HUNT-BRIDGE-00"`
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
- No source probes, downloads, extraction, model/provider calls, deployment, production-readiness claim, public-launch claim, main promotion, force-push, history rewrite, SYN implementation, DOMAIN/SCOUT implementation, or F0 implementation.
- No operator instance mutation, master-index mutation, committed public-index mutation, public fanout, or full Archive.org integration claim.

## ACCEPTANCE

- IA Hunt bridge policy, WorkUnit schema, runtime bridge, CLI, result-lane integration, examples, docs, validator, tests, and audit evidence are added.
- Dry-run plan, temp-instance bridge, operator/public/native projections, focused tests, selected tests, AIDE checks, and full unittest discovery pass.
- Evidence is written.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4754
- approx_tokens: 1189
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
