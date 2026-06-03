# AIDE Latest Task Packet

## PHASE

TSIS-00 - Temporal Semantic Interface System foundation

## GOAL

Establish Eureka's Temporal Semantic Interface System foundation while
preserving the closed root model from the latest operator correction.

## IMPLEMENTATION

- Add canonical semantic contracts for entities, actions, status, badges,
  navigation, and affordances.
- Add renderer, skin, compatibility-budget, fallback, cache-key, action, route,
  surface, and policy contracts under existing contract roots.
- Add canonical view-model contract stubs for search, result cards, object,
  need, candidate, source, evidence, and status pages.
- Add semantic and representation registries.
- Document future `runtime/surface` Surface Kernel placement without
  implementing runtime behavior in TSIS-00.
- Add docs, tests, validation, and audit evidence.
- Keep `INDEXLESS-LIVE-SEARCH-FALLBACK-00` as the next product task.

## WHY

Eureka needs one semantic product language with many negotiated
representations. The latest operator correction says yes to TSIS and no to new
top-level renderers, skins, services, apps, data, or infra roots.

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `b2a0e264 feat(task): reassess alpha after review apply`
- public launch: deferred
- next product task before TSIS correction: `INDEXLESS-LIVE-SEARCH-FALLBACK-00`

## ACCEPTANCE

- semantic contracts added
- representation supporting contracts added
- view contract stubs added
- semantic/affordance/representation registries added
- action/route/surface/policy supporting contracts added
- future Surface Kernel runtime placement documented under the existing
  runtime surface namespace
- future renderer implementation placement documented under the future Surface
  Kernel namespace
- no new top-level renderer, app, service, data, or infra roots
- TSIS validator passes
- focused contract and validator tests pass
- no runtime behavior changes
- no deployment, launch, index mutation, source call, download, OCR,
  extraction, or model call

## OUTPUT_SCHEMA

- `schema_version: tsis_00_result.v0`
- `task: TSIS-00`
- `status: pass|pass_with_warnings|partial|blocked|fail`
- contract/runtime/docs/tests/examples booleans
- contract/docs/tests booleans
- closed-root boundary booleans
- no-runtime-behavior boundary booleans
- next task recommendation

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_alpha_reassess_06_result.json`
- `control/inventory/tsis_00_result.json`
- `docs/architecture/TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md`
- `scripts/validate_temporal_semantic_interface_system.py`

## ALLOWED_PATHS

- `contracts/semantic/**`
- `contracts/representation/**`
- `contracts/action/**`
- `contracts/route/**`
- `contracts/surface/**`
- `contracts/policy/**`
- `contracts/view/**`
- `scripts/validate_temporal_semantic_interface_system.py`
- `tests/contracts/test_temporal_semantic_interface_contracts.py`
- `tests/scripts/test_validate_temporal_semantic_interface_system.py`
- `control/policies/temporal_semantic_interface_policy.json`
- `control/policies/surface_kernel_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/semantic_status_registry.json`
- `control/inventory/semantic_affordance_registry.json`
- `control/inventory/representation_profile_registry.json`
- `control/inventory/tsis_00*.json`
- `control/audits/tsis-00-v0/**`
- `docs/architecture/TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md`
- `docs/architecture/SURFACE_KERNEL.md`
- `docs/architecture/RENDERER_POLICY.md`
- `docs/reference/TEMPORAL_SEMANTIC_INTERFACE_CONTRACTS.md`
- `docs/operations/TSIS_00_RUNBOOK.md`
- `.aide/queue/TSIS-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`

## FORBIDDEN_PATHS

- top-level renderers root
- top-level skins root
- top-level services root
- top-level apps root
- top-level data root
- top-level infra root
- `eureka-instance/**`
- `instances/**`
- `../instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
- `secrets/**`
- `.env`
- raw live source responses
- raw full-discovery stdout/stderr logs
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`

## NON_GOALS

- No deployment, publishing, public launch, or readiness claim.
- No reviewed/master/public index mutation.
- No accepted truth or artifact verification claim.
- No TSIS runtime implementation in this phase.
- No live source calls, file fetches, OCR, extraction, execution, install,
  model/provider calls, source probes, broad crawler, or full unittest
  discovery.
- No top-level renderer, app, service, data, or infra root creation.

## VALIDATION

- `git diff --check`
- `python scripts/validate_temporal_semantic_interface_system.py`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_renderer_parity_harness.py`
- `python -m unittest tests.contracts.test_temporal_semantic_interface_contracts`
- `python -m unittest tests.scripts.test_validate_temporal_semantic_interface_system`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- AIDE doctor/validate/test/selftest/verify/review-pack/commit check

Full unittest discovery is not run by policy.

## TOKEN_ESTIMATE

- expected_input_tokens: 2200
- expected_output_tokens: 2200
- expected_evidence_tokens: 2600

## EVIDENCE

- `control/inventory/tsis_00_result.json`
- `control/inventory/tsis_00_validation_matrix.json`
- `control/audits/tsis-00-v0/`
- `.aide/queue/TSIS-00/README.md`

## NEXT

`INDEXLESS-LIVE-SEARCH-FALLBACK-00 - Add live metadata fallback when indexes are unavailable`
