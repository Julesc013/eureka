# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-03 - reassess alpha after local apply snapshot refresh

## GOAL

Reassess whether the read-only public alpha should proceed toward launch after
`SNAPSHOT-REFRESH-03` projected local-apply-derived limited reviewed metadata
and source-lead records.

## WHY

The snapshot now exposes four limited reviewed projections:

- existing reviewed records: 1
- limited reviewed metadata records: 1
- limited reviewed source leads: 2

This improves internal demo and review usefulness, but it does not prove public
launch readiness. Limited metadata/source-lead records are not verified
downloadable artifacts, malware-clean files, rights-cleared records, or
installable software.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/snapshot_refresh_03_result.json`
- `control/inventory/local_apply_live_metadata_result.json`
- `examples/snapshots/refresh/local_apply_live_metadata/`
- `examples/public_alpha/reassess/local_apply_live_metadata/`
- `control/audits/public-alpha-reassess-03-v0/`

## CURRENT_STATE

- total limited reviewed projection count: 4
- fixture candidates: 28
- live metadata candidates: 8
- known needs: 28
- absence summaries: 2
- launch recommended: false
- demo mode recommended: true
- internal review recommended: true
- next recommended task: `SEED-BATCH-MANUALS-SCANS-00`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-REASSESS-03/**`
- `.aide/queue/SEED-BATCH-MANUALS-SCANS-00/**`
- `.aide/queue/SEED-BATCH-DRIVER-SUPPORT-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-04/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-04/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/publication/**`
- `runtime/public_alpha/**`
- `runtime/local_eval/**`
- `runtime/gateway/**`
- `scripts/eureka_public_alpha_reassess.py`
- `scripts/eureka_public_alpha_reassess_report.py`
- `scripts/eureka_public_alpha_route_smoke.py`
- `scripts/validate_public_alpha_reassess.py`
- `tests/runtime/test_public_alpha_reassess*.py`
- `tests/operations/test_public_alpha_reassess_scripts.py`
- `tests/scripts/test_validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/local_apply_live_metadata/**`
- `examples/snapshots/refresh/local_apply_live_metadata/**`
- `control/policies/public_alpha_reassess*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess_03*.json`
- `docs/architecture/PUBLIC_ALPHA_REASSESS_03.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_03_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_03_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md`
- `docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md`
- `docs/reference/PUBLIC_ALPHA_LIMITED_REVIEWED_RECORD_REASSESSMENT.md`
- `control/audits/public-alpha-reassess-03-v0/**`

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

- No deployment or publication.
- No public launch or production readiness claim.
- No local apply execution.
- No public/master/reviewed index mutation.
- No operator instance mutation.
- No source probes or live source calls.
- No download, extraction, execution, install, emulation, or model behavior.
- No verified-download, malware-clean, rights-clearance, or artifact-verified claim.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/public_alpha/reassess_03.py`.
- Add limited-reviewed-record publication contract and policy.
- Add CLI/report flags for local-apply live metadata examples.
- Add examples, inventory matrices, audit evidence, docs, and focused tests.
- Keep launch recommendation false and route next work to manuals/scans seed batch.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- related snapshot refresh, local apply, live metadata review, live metadata pilot,
  public search UX, seed batch, review batch, scout, candidate index, query
  planner, snapshot relay, public alpha readonly, source action, architecture,
  and generated-artifact validators
- focused public alpha reassess unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- existing reviewed records: 1
- limited reviewed metadata records: 1
- limited reviewed source leads: 2
- total limited reviewed projection count: 4
- launch recommended: false
- demo mode recommended: true
- internal review recommended: true
- needs more reviewed records/domains/seed batches: true
- next recommended task: `SEED-BATCH-MANUALS-SCANS-00`
- no deployment, launch, mutation, download, extraction, model, or artifact/safety/rights claim

## EVIDENCE

- `control/inventory/public_alpha_reassess_03_result.json`
- `examples/public_alpha/reassess/local_apply_live_metadata/`
- `control/audits/public-alpha-reassess-03-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses the user-requested `PUBLIC_ALPHA_REASSESS_03` format with
validation and boundary summaries.
