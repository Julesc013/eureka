# AIDE Latest Task Packet

## PHASE

UNSPECIFIED - EUREKA-REAL-LIVE-SEARCH-HUNT-00

## GOAL

EUREKA-REAL-LIVE-SEARCH-HUNT-00

## WHY

Reset the current acceptance path from local-only/demo search to the real product slice: arbitrary live query, immediate transient web leads, deeper Hunt, safe inspection, local Preview Index persistence, restart, and local search. AIDE supports this by protecting secrets, bounding provider calls, selecting focused tests, and verifying no reviewed/public mutation.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/EUREKA-REAL-LIVE-SEARCH-HUNT-00/task.yaml`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `README.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
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
- `README.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/operations/**`
- `docs/reference/**`
- `control/inventory/**`
- `control/audits/**`
- `control/policies/**`
- `scripts/eureka.py`
- `runtime/search/**`
- `runtime/local/**`
- `runtime/index/**`
- `runtime/resolution_run/**`
- `runtime/engine/interfaces/**`
- `surfaces/web/**`
- `contracts/**`
- `tests/e2e/**`
- `tests/runtime/**`
- `tests/integration/**`
- `tests/scripts/**`
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
- `examples/**`
- `evals/**`
- `tests/**` outside the allowed test lanes above
- `scripts/**` outside `scripts/eureka.py` and validator/check repair
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, and source AIDE repository state

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `python -m unittest tests.runtime.test_live_web_search_provider -v`
- `python -m unittest tests.runtime.test_live_search_service -v`
- `python -m unittest tests.e2e.test_portable_eureka_instance -v`
- `python -m unittest tests.e2e.test_local_search_cli -v`
- `python -m unittest tests.e2e.test_local_search_server -v`
- `python -m unittest tests.e2e.test_local_search_preview_index -v`
- `python -m unittest tests.runtime.test_portable_eureka_instance -v`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
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

- No public exposure, tunnel activation, deployment, production-readiness claim, public-launch claim, main promotion, force-push, or history rewrite.
- No reviewed/master/public truth mutation or review decision recording.
- No raw provider credential, raw provider response, source AIDE state, prompt log, or local cache commits.
- No second broad-web provider family, model/agentic planner, downloads, or execution until the deterministic live-search/Hunt path is useful.

## LIVE_NETWORK_AUTHORIZATION

- Bounded local operator opt-in provider calls are authorized only for `--live` command/server modes.
- First broad-web provider: Brave Search API.
- Credential env vars: `BRAVE_SEARCH_API_KEY`, compatibility alias `BRAVE_API_KEY`.
- Provider search results are transient leads; do not persist Brave snippets, ranks, or raw responses under the standard terms.
- Persisted Hunt summaries must not contain provider URLs, snippets, ranks, raw bodies, or unresolved lead cards.
- Persist only independently fetched, policy-approved SourceObservations in later milestones.

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
- chars: 4782
- approx_tokens: 1196
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
