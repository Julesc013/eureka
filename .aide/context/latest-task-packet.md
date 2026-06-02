# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-04 - reassess alpha after manuals/scans and driver/support snapshot refresh

## GOAL

Record the product-readiness decision after `SNAPSHOT-REFRESH-04` projected the
manuals/scans and driver/support seed domains into the snapshot layer.

## WHY

The project now has four represented discovery domains and 68 candidates, but
public launch remains deferred. This task keeps that decision honest by
separating internal review usefulness from public launch readiness and routing
next work to a minimal public search UX MVP.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/snapshot_refresh_04_result.json`
- `control/inventory/public_alpha_reassess_04_result.json`
- `runtime/public_alpha/reassess_04.py`
- `scripts/validate_public_alpha_reassess.py`

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `429ded1e feat(snapshot): refresh after new seed domains`
- existing reviewed records: 1
- reviewed metadata records: 1
- reviewed source leads: 2
- total limited reviewed projection count: 4
- manuals/scans candidates: 16
- driver/support candidates: 16
- total candidates: 68
- represented domains: `frontier_resolution_media`, `legacy_software`,
  `manuals_docs_scans`, `driver_support_media`
- public search view models: available
- public search UX MVP: not implemented

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-REASSESS-04/**`
- `.aide/queue/PUBLIC-SEARCH-UX-MVP-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `contracts/publication/**`
- `runtime/public_alpha/**`
- `scripts/eureka_public_alpha_reassess.py`
- `scripts/eureka_public_alpha_reassess_report.py`
- `scripts/eureka_public_alpha_route_smoke.py`
- `scripts/validate_public_alpha_reassess.py`
- `tests/runtime/test_public_alpha_reassess*.py`
- `tests/operations/test_public_alpha_reassess_scripts.py`
- `tests/scripts/test_validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/manuals_scans_driver_support/**`
- `control/policies/public_alpha_reassess*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess_04*.json`
- `control/audits/public-alpha-reassess-04-v0/**`
- `docs/architecture/PUBLIC_ALPHA_REASSESS_04.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_04_RUNBOOK.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_04_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_DOMAIN_COVERAGE_REASSESSMENT.md`
- `docs/reference/PUBLIC_ALPHA_UX_READINESS_REASSESSMENT.md`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `../instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- raw live source responses
- raw IA responses
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## NON_GOALS

- No deployment, publication, public launch, or readiness claim.
- No accepted truth, automatic candidate acceptance, or reviewed/master/public index mutation.
- No operator instance mutation.
- No live source calls, downloads, file fetches, OCR, extraction, install, or execution.
- No model/provider calls, raw live responses, or public live source fanout.
- No verified-download, malware-clean, compatibility, scan-completeness,
  OCR-quality, or rights-clearance claims.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/public_alpha/reassess_04.py`.
- Extend public-alpha reassess CLI and report CLI for manuals/driver examples.
- Add domain coverage and UX readiness contracts, policies, examples,
  inventory, audit evidence, docs, validator checks, and focused tests.
- Keep launch deferred and route next work to `PUBLIC-SEARCH-UX-MVP-00`.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- snapshot, seed-batch, local-apply, review-batch, SCOUT, candidate-index,
  query-planner, public-search UX, public-alpha readonly, source-action,
  architecture, generated-artifact validators
- focused public-alpha reassess unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- public launch recommended: false
- demo mode recommended: true
- internal review recommended: true
- total limited reviewed projection count: 4
- total candidate count: 68
- represented domain count: 4
- public search view models available: true
- public search UX MVP implemented: false
- next recommended task: `PUBLIC-SEARCH-UX-MVP-00`

## EVIDENCE

- `control/inventory/public_alpha_reassess_04_result.json`
- `examples/public_alpha/reassess/manuals_scans_driver_support/`
- `control/audits/public-alpha-reassess-04-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses `STATUS`, `SUMMARY`, `PUBLIC_ALPHA_REASSESS_04`,
`VALIDATION`, `BOUNDARIES`, and `NEXT_TASK`.
