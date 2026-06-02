# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-04 - refresh snapshots after manuals/scans and driver/support batches

## GOAL

Project the manuals/scans and driver/support seed-batch outputs into the
snapshot, relay, public search view-model, and public-alpha reassessment input
lanes while preserving all review-only and non-claim boundaries.

## WHY

`PUBLIC-ALPHA-REASSESS-03` kept public launch deferred and asked for safer
third-domain corpus growth. Manuals/scans and driver/support seed batches are
now complete, so snapshot packaging must make those new candidates visible
without converting metadata candidates into reviewed truth, fetched documents,
driver downloads, OCR text, compatibility guarantees, safety claims, or rights
clearance.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_reassess_03_result.json`
- `control/inventory/snapshot_refresh_03_result.json`
- `control/inventory/seed_batch_manuals_scans_result.json`
- `control/inventory/seed_batch_driver_support_result.json`
- `runtime/snapshots/refresh_04.py`
- `scripts/validate_snapshot_refresh.py`

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `0373fdbd feat(seed): add driver support discovery batch`
- public alpha launch recommended: false
- limited reviewed projection count remains 4
- manuals/scans candidates: 16
- driver/support candidates: 16
- expected total candidates after live metadata: 68

## ALLOWED_PATHS

- `.aide/queue/SNAPSHOT-REFRESH-04/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-04/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `contracts/snapshot/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/validate_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh*.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/manuals_scans_driver_support/**`
- `examples/relay/refresh/**`
- `examples/public_alpha/reassess/manuals_scans_driver_support/**`
- `control/policies/snapshot_refresh*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh_04*.json`
- `control/audits/snapshot-refresh-04-v0/**`
- `docs/architecture/SNAPSHOT_REFRESH_04.md`
- `docs/architecture/SNAPSHOT_MANUALS_SCANS_SECTION.md`
- `docs/architecture/SNAPSHOT_DRIVER_SUPPORT_SECTION.md`
- `docs/operations/SNAPSHOT_REFRESH_04_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_04_PLAN.md`
- `docs/reference/SNAPSHOT_MANUALS_SCANS_SECTION.md`
- `docs/reference/SNAPSHOT_DRIVER_SUPPORT_SECTION.md`

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
- No live source calls, downloads, file fetches, OCR, extraction, install or execution.
- No model/provider calls, raw live responses, or public live source fanout.
- No verified-download, malware-clean, compatibility, scan-completeness,
  OCR-quality, or rights-clearance claims.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/snapshots/refresh_04.py`.
- Extend snapshot refresh CLI and report CLI with `--from-manuals-driver-examples`.
- Add manuals/scans and driver/support snapshot contracts, policies, examples,
  inventory, audit evidence, docs, validator checks, and focused tests.
- Keep new seed outputs as metadata-only, review-required candidate sections.
- Route next work to `PUBLIC-ALPHA-REASSESS-04`.

## VALIDATION

- `git diff --check`
- `python scripts/validate_snapshot_refresh.py`
- seed-batch, public-alpha, local-apply, review-batch, SCOUT, candidate-index,
  query-planner, public-search UX, public-alpha readonly, source-action,
  architecture, generated-artifact validators
- focused snapshot refresh unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- manuals/scans candidates projected: 16
- driver/support candidates projected: 16
- additional seed candidates projected: 32
- total candidate count projected: 68
- limited reviewed projection count remains 4
- no download, file fetch, OCR, extraction, install, model, site/dist, deployment,
  mutation, launch, readiness, safety, compatibility, scan-completeness,
  OCR-quality, or rights-clearance claim
- next recommended task: `PUBLIC-ALPHA-REASSESS-04`

## EVIDENCE

- `control/inventory/snapshot_refresh_04_result.json`
- `examples/snapshots/refresh/manuals_scans_driver_support/`
- `control/audits/snapshot-refresh-04-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses `STATUS`, `SUMMARY`, `SNAPSHOT_REFRESH_04`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.
