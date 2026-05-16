# AIDE Verification Report

## VERIFIER_RESULT

- result: WARN
- method: deterministic repo-local checks
- contents_inline: false
- provider_or_model_calls: none

## CHECK_COUNTS

- info: 138
- warnings: 9
- errors: 0
- checked_files: 75
- changed_files: 17

## CHANGED_FILES

- unknown: `.aide/changelog/CHANGELOG.preview.md` (M; does not match active task allowed paths)
- unknown: `.aide/changelog/RELEASE_NOTES.preview.md` (M; does not match active task allowed paths)
- unknown: `.aide/changelog/changelog.preview.json` (M; does not match active task allowed paths)
- unknown: `.aide/changelog/malformed-commits.md` (M; does not match active task allowed paths)
- allowed: `.aide/context/latest-task-packet.md` (M; matches active task allowed path)
- allowed: `.aide/evals/runs/latest-golden-tasks.json` (M; matches active task allowed path)
- allowed: `.aide/evals/runs/latest-golden-tasks.md` (M; matches active task allowed path)
- unknown: `.aide/git/latest-helper-plan.json` (M; does not match active task allowed paths)
- unknown: `.aide/git/latest-helper-plan.md` (M; does not match active task allowed paths)
- unknown: `.aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01` (??; does not match active task allowed paths)
- allowed: `.aide/reports/eureka-aide-preservation-plan.md` (??; matches active task allowed path)
- allowed: `.aide/reports/eureka-existing-tool-preflight.md` (??; matches active task allowed path)
- allowed: `.aide/reports/eureka-fresh-upgrade-preflight.md` (??; matches active task allowed path)
- allowed: `.aide/reports/eureka-next-aide-task.md` (??; matches active task allowed path)
- allowed: `.aide/reports/eureka-product-boundary-preservation.md` (??; matches active task allowed path)
- allowed: `.aide/reports/eureka-release-bundle-readiness.md` (??; matches active task allowed path)
- unknown: `native/win/winforms/src/Eureka/obj` (??; does not match active task allowed paths)

## WARNINGS

- file_references: referenced path does not exist (from .aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01/evidence/evidence-packet.md) `origin/dev`
- diff_scope: does not match active task allowed paths `.aide/changelog/CHANGELOG.preview.md`
- diff_scope: does not match active task allowed paths `.aide/changelog/RELEASE_NOTES.preview.md`
- diff_scope: does not match active task allowed paths `.aide/changelog/changelog.preview.json`
- diff_scope: does not match active task allowed paths `.aide/changelog/malformed-commits.md`
- diff_scope: does not match active task allowed paths `.aide/git/latest-helper-plan.json`
- diff_scope: does not match active task allowed paths `.aide/git/latest-helper-plan.md`
- diff_scope: does not match active task allowed paths `.aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01`
- diff_scope: does not match active task allowed paths `native/win/winforms/src/Eureka/obj`

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
- `.aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01/evidence/evidence-packet.md`
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
