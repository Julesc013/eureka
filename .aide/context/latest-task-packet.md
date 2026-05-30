# AIDE Latest Task Packet

## PHASE

UNSPECIFIED - SCOUT-RUNTIME-00

## GOAL

SCOUT-RUNTIME-00

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

- `.aide/**`
- `AGENTS.md`
- `docs/architecture/**`
- `docs/operations/**`
- `docs/reference/**`
- `control/inventory/**`
- `control/audits/**`
- `control/policies/**`
- `contracts/scout/**`
- `contracts/discovery/**`
- `contracts/candidates/**`
- `contracts/search/query_plan/**`
- `contracts/source/action/**`
- `contracts/review/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `contracts/local_apply/**`
- `contracts/instances/**`
- `contracts/workunit/**`
- `contracts/domain/**`
- `runtime/gateway/public_api/**`
- `runtime/gateway/tests/**`
- `runtime/scout/**`
- `runtime/discovery/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/candidates/**`
- `runtime/search/query_plan/**`
- `runtime/source/action/**`
- `runtime/connectors/internet_archive_metadata/**`
- `runtime/review/queue/**`
- `runtime/resolution_run/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/gateway/**`
- `runtime/local_eval/**`
- `runtime/workunit_queue/**`
- `runtime/source/observation/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `examples/candidates/**`
- `examples/candidate_index/**`
- `examples/search/candidate_lanes/**`
- `examples/public_alpha/**`
- `examples/public_alpha/candidates/**`
- `examples/public_alpha/scout/**`
- `examples/scout/**`
- `examples/discovery/**`
- `examples/query_plans/**`
- `examples/sources/internet_archive_metadata/**`
- `scripts/eureka_scout_runtime.py`
- `scripts/eureka_scout_trails.py`
- `scripts/eureka_scout_relations.py`
- `scripts/eureka_scout_source_trust.py`
- `scripts/validate_scout_runtime.py`
- `scripts/eureka_candidate_index.py`
- `scripts/eureka_candidate_search.py`
- `scripts/eureka_candidate_ingest.py`
- `scripts/eureka_candidate_review_handoff.py`
- `scripts/eureka_query_plan.py`
- `scripts/local_queue_progress.py`
- `scripts/validate_*.py`
- `scripts/check_*.py`
- `tests/runtime/**`
- `tests/operations/**`
- `tests/scripts/**`
- `tests/aide/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `runtime/**` unless covered by allowed paths above
- `contracts/**` unless covered by allowed paths above
- `surfaces/**` unless covered by allowed paths above
- `site/**`
- `native/**`
- `crates/**`
- `examples/**` unless covered by allowed paths above
- `evals/**`
- `tests/**` unless covered by allowed paths above
- `scripts/**` unless covered by allowed paths above
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
- `py -3 .aide/scripts/aide_lite.py pack --task "SCOUT-RUNTIME-00"`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/validate_scout_runtime.py`
- `python scripts/validate_candidate_index_runtime.py`
- `python scripts/validate_query_to_source_action_planner.py`
- focused SCOUT and candidate-index unittest modules
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

- No downloads, extraction, installs, uploads, accounts, telemetry, production-readiness claim, public-launch claim, deployment, main promotion, force-push, history rewrite, SYN implementation, or F0 implementation.
- No source-cache mutation, evidence-ledger mutation, candidate promotion, reviewed-index mutation, public-index mutation, local-index mutation, master-index mutation, live source calls, crawling, scraping, or SCOUT accepted-truth claims.
- No model/provider calls, live model routing, local model setup, exact tokenizer, provider billing ledger, Commander, Mobile, MCP/A2A, or autonomous loop unless a future reviewed queue item explicitly authorizes it.

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
- chars: 4786
- approx_tokens: 1197
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
