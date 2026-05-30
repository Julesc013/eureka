# AIDE Latest Task Packet

## PHASE

UNSPECIFIED - SEED-BATCH-LEGACY-SOFTWARE-00

## GOAL

SEED-BATCH-LEGACY-SOFTWARE-00

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
- `contracts/seed_batches/**`
- `docs/architecture/**`
- `docs/operations/**`
- `docs/reference/**`
- `control/inventory/**`
- `control/audits/**`
- `control/policies/**`
- `runtime/seed_batches/**`
- `examples/seed_batches/**`
- `examples/seed_batches/legacy_software/**`
- `examples/query_plans/legacy_software/**`
- `examples/candidates/legacy_software/**`
- `examples/scout/legacy_software/**`
- `examples/review_batch/legacy_software/**`
- `examples/public_alpha/legacy_software/**`
- `scripts/local_queue_progress.py`
- `scripts/validate_*.py`
- `scripts/check_*.py`
- `scripts/eureka_seed_batch_legacy_software.py`
- `scripts/eureka_seed_batch_run.py`
- `scripts/eureka_seed_batch_report.py`
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
- `py -3 .aide/scripts/aide_lite.py pack --task "SEED-BATCH-LEGACY-SOFTWARE-00"`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `python scripts/validate_seed_batch_legacy_software.py`
- `python scripts/validate_seed_batch_frontier_media.py`
- `python scripts/validate_review_batch.py`
- `python scripts/validate_scout_runtime.py`
- `python scripts/validate_candidate_index_runtime.py`
- `python scripts/validate_query_to_source_action_planner.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_source_action_kernel.py`
- `python scripts/validate_source_wave.py`
- `python scripts/validate_domain_packs.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- focused SEED-BATCH-LEGACY-SOFTWARE unittest modules
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

- No deployment, publishing, production-readiness claim, public-launch claim, main promotion, force-push, history rewrite, broad crawling, arbitrary scraping, downloads, uploads, extraction, execution, install/emulation, model/provider calls, package download, software safety claim, crack/keygen/serial support, or full discovery inside AI sessions.
- No automatic candidate acceptance, reviewed-index mutation, master/public index mutation, public mutation, operator instance mutation by default, local apply execution, snapshot refresh execution, or raw live metadata response commits.

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
- chars: 4778
- approx_tokens: 1195
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
