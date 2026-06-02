# AIDE Latest Task Packet

## PHASE

PUBLIC-SEARCH-UX-MVP-00 - implement minimal no-JS public search UX over view models

## GOAL

Render a search-first, no-JS, read-only public search UX from existing public
search view-model projections.

## WHY

`PUBLIC-ALPHA-REASSESS-04` kept public launch deferred and identified a public
search UX MVP as the next useful step. The project has four represented
discovery domains and 68 candidates, but view models alone are not a usable
public search surface.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_alpha_reassess_04_result.json`
- `control/inventory/snapshot_refresh_04_result.json`
- `examples/snapshots/refresh/manuals_scans_driver_support/public_search_view_model_projection.json`
- `runtime/public_search/ux_mvp.py`
- `scripts/validate_public_search_ux_mvp.py`

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `496ab9e0 feat(task): reassess alpha after new seed domains`
- public launch: deferred
- represented domains: 4
- total candidates after seed domains: 68
- total limited reviewed projection count: 4
- public search UX MVP: implemented as read-only examples, not deployed

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-SEARCH-UX-MVP-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-05/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `contracts/view/models/public_search/**`
- `runtime/public_search/**`
- `scripts/eureka_public_search_render.py`
- `scripts/eureka_public_search_ux_smoke.py`
- `scripts/eureka_public_search_route_smoke.py`
- `scripts/validate_public_search_ux_mvp.py`
- `tests/runtime/test_public_search*.py`
- `tests/operations/test_public_search_ux_mvp_scripts.py`
- `tests/scripts/test_validate_public_search_ux_mvp.py`
- `examples/public_search_ux/**`
- `control/policies/public_search*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_search_ux_mvp*.json`
- `control/audits/public-search-ux-mvp-00-v0/**`
- `docs/architecture/PUBLIC_SEARCH_UX_MVP.md`
- `docs/architecture/PUBLIC_SEARCH_RESULT_CARD.md`
- `docs/operations/PUBLIC_SEARCH_UX_MVP_RUNBOOK.md`
- `docs/operations/POST_PUBLIC_SEARCH_UX_MVP_PLAN.md`
- `docs/reference/PUBLIC_SEARCH_PAGE.md`
- `docs/reference/PUBLIC_SEARCH_RESULT_CARD.md`
- `docs/reference/PUBLIC_SEARCH_STATUS_BADGES.md`
- `docs/reference/PUBLIC_SEARCH_NO_RESULTS.md`

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

- Add `runtime/public_search/ux_mvp.py` and package exports.
- Extend public-search result-card contracts with MVP fields and limited states.
- Add no-JS render/smoke CLIs, validator, examples, inventories, audit evidence,
  docs, and focused tests.
- Keep old `PUBLIC-SEARCH-UX-MODEL-00` validator/tests passing.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_search_ux_mvp.py`
- public search UX model, public alpha reassess, snapshot refresh, seed batch,
  public-alpha read-only, snapshot relay, source-action, architecture, and
  generated-artifact validators
- focused public search UX MVP unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- no-JS GET search form passes
- candidate and verified records remain visibly distinct
- limited reviewed metadata/source-lead records remain distinct from verified artifacts
- public projection is read-only
- no deployment, public launch, site/dist write, public mutation, download,
  extraction, or model/provider call
- next recommended task: `SNAPSHOT-REFRESH-05`

## EVIDENCE

- `control/inventory/public_search_ux_mvp_result.json`
- `examples/public_search_ux/`
- `control/audits/public-search-ux-mvp-00-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses `STATUS`, `SUMMARY`, `PUBLIC_SEARCH_UX_MVP`,
`VALIDATION`, `BOUNDARIES`, and `NEXT_TASK`.
