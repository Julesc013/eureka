# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-05 - reassess alpha after public search UX projection refresh

## GOAL

Reassess the read-only public alpha after `SNAPSHOT-REFRESH-05` projected the
public search UX MVP into snapshot, relay, and public-alpha reassessment inputs.

## WHY

The no-JS public search UX MVP is now present in public-safe examples. The
product decision needs to record that usefulness improved, while preserving the
launch boundary because the reviewed corpus is still small and no external full
discovery, main promotion, or launch approval has occurred.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_search_ux_mvp_result.json`
- `control/inventory/snapshot_refresh_05_result.json`
- `runtime/public_alpha/reassess_05.py`
- `scripts/validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/public_search_ux_mvp/`

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `9f643c97 feat(snapshot): refresh public search UX projections`
- public launch: deferred
- total limited reviewed projection count: 4
- total candidate count: 68
- public UX routes: 8
- result-card states: 8
- public search UX MVP: implemented and verified in read-only examples

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-REASSESS-05/**`
- `.aide/queue/REVIEW-BATCH-APPLY-NEXT-00/**`
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
- `examples/public_alpha/reassess/public_search_ux_mvp/**`
- `control/policies/public_alpha_reassess*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess_05*.json`
- `control/audits/public-alpha-reassess-05-v0/**`
- `docs/architecture/PUBLIC_ALPHA_REASSESS_05.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_05_RUNBOOK.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_05_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_UX_MVP_REASSESSMENT.md`

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

- Add public alpha reassess 05 runtime over snapshot refresh 05 plus UX MVP evidence.
- Add UX MVP reassessment contract and explicit full-discovery/promotion policies.
- Generate metrics, route, domain, candidate, UX MVP, blocker, next-work, boundary, inventory, and audit evidence.
- Extend public alpha reassess CLI, report CLI, validator, docs, and focused tests.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- snapshot refresh, public search UX MVP, public search UX model, seed batch,
  public-alpha read-only, snapshot relay, architecture, and generated-artifact validators
- focused public alpha reassess unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- UX MVP is verified and improves internal demo/review usefulness.
- `launch_recommended` remains false.
- `needs_review_batch_apply_next`, `needs_external_full_discovery`,
  `needs_main_promotion_before_launch`, and
  `needs_public_alpha_launch_approval` are true.
- No site/dist write, deployment, public launch, mutation, live call, download,
  file fetch, OCR, extraction, model/provider use, or readiness claim.

## EVIDENCE

- `control/inventory/public_alpha_reassess_05_result.json`
- `control/inventory/public_alpha_reassess_05_validation_matrix.json`
- `control/audits/public-alpha-reassess-05-v0/`
- `examples/public_alpha/reassess/public_search_ux_mvp/`

## OUTPUT_SCHEMA

Final result shape follows `public_alpha_reassess_05_result.v0` and reports the
UX MVP evidence, blocker register, boundary flags, and recommended next task.

## TOKEN_ESTIMATE

- latest task packet: under 2000 tokens
- latest context packet: use `.aide/context/latest-context-packet.md`
- full discovery: not run by policy
