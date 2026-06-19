# AIDE Latest Task Packet

## PHASE

runtime-architecture-boundary-repair - SOURCE-FOUNDRY-RUNTIME-LEAKAGE-REPAIR-00

## GOAL

Clear the current runtime architecture leakage gate by classifying and repairing
new unallowlisted production-path vocabulary findings without changing product
semantics, weakening public/truth boundaries, or bulk-allowlisting architecture
debt.

## WHY

The Source Foundry full-discovery drift repair found a material static
runtime-naming gate failure: 52 new unallowlisted production-path findings. The
previous validation-drift packet protected runtime paths, so this dedicated
parallel repair authority is required before historical validator drift repair
or another external full-discovery rerun.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/architecture/RUNTIME_NAMING_BOUNDARY.md`
- `docs/operations/R0_RUNTIME_LEAKAGE_GATE.md`
- `control/policies/runtime_architecture_leakage_policy.json`
- `control/policies/runtime_architecture_leakage_allowlist.json`
- `control/audits/validation/source_foundry_preview_v0_drift_repair_01/UNKNOWN_GROUP_INVESTIGATION.md`
- `.aide/queue/SOURCE-FOUNDRY-RUNTIME-LEAKAGE-REPAIR-00/task.yaml`
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

- `.aide/queue/SOURCE-FOUNDRY-RUNTIME-LEAKAGE-REPAIR-00/**`
- `.aide/context/**`
- `runtime/local/**`
- `runtime/local/__init__.py`
- `scripts/**`
- `tools/auditors/audit_runtime_architecture_leakage.py`
- `tools/validators/validate_runtime_architecture_leakage.py`
- `control/policies/**`
- `control/inventory/runtime_architecture_leakage_*.json`
- `control/audits/r0-02-runtime-architecture-leakage-gate-v0/**`
- `control/audits/validation/source_foundry_runtime_leakage_repair_00/**`
- `docs/architecture/RUNTIME_NAMING_BOUNDARY.md`
- `docs/operations/R0_RUNTIME_LEAKAGE_GATE.md`
- `tests/operations/**`
- `tests/runtime/**`
- `tests/e2e/**`
- `tests/scripts/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `runtime/connectors/**`
- `runtime/gateway/**`
- `examples/**`
- `evals/**`
- `release/**`
- `archive/**`
- `LICENSE.md`
- `LICENSE-SUMMARY.md`
- `NOTICE.md`
- `README.md`
- `.aide/queue/index.yaml`
- reviewed-record materialization paths
- reviewed/master/public index stores
- review decisions and review stores
- snapshots/public projections
- public exposure, tunnel, hosting, or launch code except import-only changes caused by an authorized runtime/local rename
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, and source AIDE repository state

## IMPLEMENTATION

- Capture a fresh leakage baseline and disposition every new finding.
- Prefer domain vocabulary renames over allowlist changes.
- Use `git mv` for authorized runtime/local module renames.
- Preserve product behavior, CLI commands, review/truth boundaries, and public exposure posture.
- Use exact temporary allowlist entries only as a last resort, with owner, replacement, expiry, and no wildcards.
- Do not run full unittest discovery inside the AI session.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `python scripts/audit_runtime_architecture_leakage.py --check --json`
- `python scripts/validate_runtime_architecture_leakage.py --json`
- `python -m unittest tests.operations.test_legacy_runtime_leakage_remediation tests.operations.test_runtime_architecture_leakage -v`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- focused tests selected by changed runtime modules
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

- No product feature behavior change.
- No review decision changes, reviewed records, reviewed/master mutation, public-index mutation, review-store mutation, or snapshot refresh.
- No source probes, downloads, file fetches, Wayback replay, provider/network/model calls, deployment, public exposure, public launch, production-readiness claim, main promotion, force-push, or license change.
- No blanket allowlist, wildcard runtime allowlist, permanent allowlist entries, or ignored failing tests.

## ACCEPTANCE

- Leakage baseline and finding disposition matrix are recorded.
- Final leakage audit has zero new unallowlisted findings.
- Runtime leakage validator and targeted tests pass, or the task stops with an explicit larger-refactor blocker.
- Behaviour parity is documented for changed modules.
- Public/truth/index/provider boundaries remain unchanged.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4800
- approx_tokens: 1200
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
