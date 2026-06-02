# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-05 - refresh public projections after UX MVP

## GOAL

Package the current four-domain snapshot plus the public search UX MVP into a
read-only snapshot/relay/public-alpha reassessment projection set.

## WHY

`PUBLIC-SEARCH-UX-MVP-00` added a no-JS public search UX over existing public
search view models. The snapshot layer now needs a projection refresh so the UX
routes, result cards, no-results state, and text/classic examples are visible to
the next product-readiness reassessment.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_search_ux_mvp_result.json`
- `control/inventory/snapshot_refresh_04_result.json`
- `examples/public_search_ux/`
- `runtime/public_search/ux_mvp.py`
- `runtime/snapshots/refresh_05.py`
- `scripts/validate_snapshot_refresh.py`

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `ebc7b02b feat(public): add search UX MVP`
- public launch: deferred
- represented domains: 4
- total candidates after seed domains: 68
- total limited reviewed projection count: 4
- public search UX MVP: implemented as read-only examples, not deployed

## ALLOWED_PATHS

- `.aide/queue/SNAPSHOT-REFRESH-05/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-05/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `contracts/snapshot/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/public_alpha/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/validate_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh*.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/public_search_ux_mvp/**`
- `examples/relay/refresh/public_search_ux_mvp_refreshed_relay_projection.json`
- `examples/public_alpha/reassess/public_search_ux_mvp/**`
- `control/policies/snapshot_refresh*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh_05*.json`
- `control/audits/snapshot-refresh-05-v0/**`
- `docs/architecture/SNAPSHOT_REFRESH_05.md`
- `docs/architecture/SNAPSHOT_PUBLIC_SEARCH_UX_PROJECTION.md`
- `docs/architecture/SNAPSHOT_RESULT_CARD_PROJECTION.md`
- `docs/operations/SNAPSHOT_REFRESH_05_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_05_PLAN.md`
- `docs/reference/SNAPSHOT_PUBLIC_SEARCH_UX_SECTION.md`
- `docs/reference/SNAPSHOT_RESULT_CARD_SECTION.md`
- `docs/reference/SNAPSHOT_NO_RESULTS_SECTION.md`

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
- No live source calls, public live source fanout, downloads, file fetches, OCR, extraction, install, or execution.
- No model/provider calls or raw live responses.
- No verified-download, malware-clean, compatibility, scan-completeness, OCR-quality, or rights-clearance claims.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add snapshot refresh 05 runtime over refresh 04 plus public search UX MVP handoff.
- Add public UX, route, result-card, no-results, text, relay, and reassess projection sections.
- Extend snapshot refresh CLI/report/validator support.
- Generate examples, inventory, audit pack, docs, and focused tests.

## VALIDATION

- `git diff --check`
- `python scripts/validate_snapshot_refresh.py`
- public search UX MVP, public search UX model, public alpha reassess, seed batch,
  public-alpha read-only, snapshot relay, architecture, and generated-artifact validators
- focused snapshot refresh 05 unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- public search UX integrated into snapshot refresh 05
- 8 public UX routes and 8 result-card states projected
- public projection remains no-JS and read-only
- total limited reviewed projection count remains 4
- total candidate count remains 68
- no site/dist write, deployment, public launch, or readiness claim

## EVIDENCE

- `control/inventory/snapshot_refresh_05_result.json`
- `control/inventory/snapshot_refresh_05_validation_matrix.json`
- `control/audits/snapshot-refresh-05-v0/`
- `examples/snapshots/refresh/public_search_ux_mvp/`

## OUTPUT_SCHEMA

Final result shape follows `snapshot_refresh_05_result.v0` and reports the
projection counts, validation status, boundary flags, and recommended next task.

## TOKEN_ESTIMATE

- latest task packet: under 1600 tokens
- latest context packet: use `.aide/context/latest-context-packet.md`
- full discovery: not run by policy
