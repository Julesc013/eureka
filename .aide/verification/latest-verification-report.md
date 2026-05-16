# AIDE Verification Report

## VERIFIER_RESULT

- result: PASS
- method: deterministic repo-local checks
- contents_inline: false
- provider_or_model_calls: none

## CHECK_COUNTS

- info: 105
- warnings: 0
- errors: 0
- checked_files: 74
- changed_files: 3

## CHANGED_FILES

- allowed: `.aide/context/latest-review-packet.md` (M; matches active task allowed path)
- allowed: `.aide/reports/token-ledger.jsonl` (M; matches active task allowed path)
- allowed: `.aide/reports/token-savings-summary.md` (M; matches active task allowed path)

## WARNINGS

- none

## ERRORS

- none

## EVIDENCE_REFS

- `.aide.local.example/README.md`
- `.aide.local.example/cache/README.md`
- `.aide.local.example/config.example.yaml`
- `.aide.local.example/ledgers/README.md`
- `.aide.local.example/traces/README.md`
- `.aide/cache/README.md`
- `.aide/cache/key-policy.yaml`
- `.aide/cache/latest-cache-keys.json`
- `.aide/cache/latest-cache-keys.md`
- `.aide/context/compiler.yaml`
- `.aide/context/context-index.json`
- `.aide/context/excerpt-policy.yaml`
- `.aide/context/ignore.yaml`
- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/priority.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/repo-map.md`
- `.aide/context/test-map.json`
- `.aide/controller/README.md`
- `.aide/controller/failure-taxonomy.yaml`
- `.aide/controller/latest-outcome-report.md`
- `.aide/controller/latest-recommendations.md`
- `.aide/controller/outcome-ledger.jsonl`
- `.aide/gateway`
- `.aide/gateway/README.md`
- `.aide/gateway/architecture.md`
- `.aide/gateway/endpoints.yaml`
- `.aide/gateway/latest-gateway-status.json`
- `.aide/gateway/latest-gateway-status.md`
- `.aide/gateway/lifecycle.yaml`
- `.aide/gateway/security-boundary.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/memory/project-state.md`
- `.aide/models/README.md`
- `.aide/models/capabilities.yaml`
- `.aide/models/fallback.yaml`
- `.aide/models/hard-floors.yaml`
- `.aide/models/providers.yaml`
- `.aide/models/routes.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/controller.yaml`
- `.aide/policies/gateway.yaml`
- `.aide/policies/local-state.yaml`
- `.aide/policies/provider-adapters.yaml`
- `.aide/policies/routing.yaml`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/verification.yaml`
- `.aide/prompts/codex-token-mode.md`
- `.aide/prompts/compact-task.md`
- `.aide/prompts/evidence-review.md`
- `.aide/providers`
- `.aide/providers/adapter-contract.yaml`
- `.aide/providers/capability-matrix.yaml`
- `.aide/providers/latest-provider-status.json`
- `.aide/providers/latest-provider-status.md`
- `.aide/providers/provider-catalog.yaml`
- `.aide/providers/status.yaml`
- `.aide/routing/README.md`
- `.aide/routing/latest-route-decision.json`
- `.aide/routing/latest-route-decision.md`
- `.aide/routing/route-decision.schema.json`
- `.aide/scripts/aide_lite.py`
- `.aide/verification/diff-scope-policy.yaml`
- `.aide/verification/evidence-packet.template.md`
- `.aide/verification/file-reference-policy.yaml`
- `.aide/verification/review-decision-policy.yaml`
- `.aide/verification/review-packet.template.md`
- `.aide/verification/secret-scan-policy.yaml`
- `.gitignore`
- `AGENTS.md`
- `README.md`

## LIMITS

- Structural verifier only; no LLM judging.
- Diff scope is path-based only.
- Secret scan is heuristic only.
- Token counts use chars / 4 approximation.
