# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-06 - reassess alpha after review batch apply snapshot refresh

## GOAL

Reassess public-alpha launch/defer posture after `SNAPSHOT-REFRESH-06` projected
review-batch apply outputs into snapshot, relay, public-search, and public-alpha
handoffs.

## IMPLEMENTATION

- Extend the public-alpha reassess runtime with a deterministic
  `PUBLIC-ALPHA-REASSESS-06` examples path.
- Project snapshot-refresh-06 and review-batch-apply evidence into metrics,
  launch blockers, resilience gaps, next-work recommendations, examples,
  inventory files, and an audit pack.
- Preserve all non-launch and non-mutation boundaries while routing follow-up
  work to indexless live search fallback and search usefulness evaluation.

## WHY

The reviewed corpus grew from 4 to 12 limited reviewed projections. That is
materially more useful for internal demo and review, but it is still below the
25-record launch threshold and lacks resilience/search-usefulness gates.

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `47425906 feat(snapshot): refresh after review batch apply`
- public launch: deferred
- snapshot refresh 06: pass
- review batch apply next: pass
- public search UX MVP: pass

## ACCEPTANCE

- previous limited reviewed projection count: 4
- new reviewed record delta count: 8
- total limited reviewed projection count: 12
- reviewed known need count: 2
- reviewed bounded absence count: 2
- candidate count after apply: 60
- domain count: 4
- public UX route count: 8
- result-card states count: 8
- launch recommended: false
- reviewed corpus growth confirmed: true
- indexless live fallback implemented: false
- search usefulness eval implemented: false

## OUTPUT_SCHEMA

- `schema_version: public_alpha_reassess_06_result.v0`
- `task: PUBLIC-ALPHA-REASSESS-06`
- `status: pass|pass_with_warnings|partial|blocked|fail`
- counts for limited reviewed projections, reviewed known needs, reviewed
  bounded absences, candidates, domains, routes, and result-card states
- launch/defer decision flags
- next-work recommendation
- boundary flags with deployment, launch, mutation, download, extraction,
  model, and readiness claims set false

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/snapshot_refresh_06_result.json`
- `control/inventory/review_batch_apply_next_result.json`
- `control/inventory/public_search_ux_mvp_result.json`
- `examples/public_alpha/reassess/review_batch_apply/`
- `runtime/public_alpha/reassess_06.py`
- `scripts/validate_public_alpha_reassess.py`

## ALLOWED_PATHS

- `contracts/publication/**`
- `runtime/public_alpha/**`
- `runtime/gateway/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/public_search/**`
- `scripts/eureka_public_alpha_reassess.py`
- `scripts/eureka_public_alpha_reassess_report.py`
- `scripts/eureka_public_alpha_route_smoke.py`
- `scripts/validate_public_alpha_reassess.py`
- `tests/runtime/test_public_alpha_reassess*.py`
- `tests/operations/test_public_alpha_reassess_scripts.py`
- `tests/scripts/test_validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/review_batch_apply/**`
- `control/policies/public_alpha_reassess*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess_06*.json`
- `control/audits/public-alpha-reassess-06-v0/**`
- `docs/architecture/PUBLIC_ALPHA_REASSESS_06.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_06_RUNBOOK.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_06_PLAN.md`
- `docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md`
- `docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md`
- `docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md`
- `docs/reference/PUBLIC_ALPHA_REVIEW_BATCH_APPLY_REASSESSMENT.md`
- `docs/reference/PUBLIC_ALPHA_RESILIENCE_GAP_REASSESSMENT.md`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-06/**`
- `.aide/queue/INDEXLESS-LIVE-SEARCH-FALLBACK-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`

## FORBIDDEN_PATHS

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
- `native/**`
- `crates/**`

## NON_GOALS

- No deployment, publishing, public launch, or readiness claim.
- No reviewed/master/public index mutation.
- No operator instance mutation.
- No accepted truth or artifact verification claim.
- No verified download, malware-clean, compatibility, rights-clearance,
  scan-completeness, or OCR-quality claim.
- No live source calls, file fetches, OCR, extraction, execution, install,
  model/provider calls, source probes, broad crawler, or full unittest discovery.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- `python scripts/validate_snapshot_refresh.py`
- `python scripts/validate_review_batch_apply_next.py`
- `python scripts/validate_public_search_ux_mvp.py`
- `python scripts/validate_public_search_ux_model.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- focused public-alpha reassess unittest modules
- AIDE doctor/validate/test/selftest/verify/review-pack/commit check

Full unittest discovery is not run by policy.

## TOKEN_ESTIMATE

- expected_input_tokens: 1500
- expected_output_tokens: 1800
- expected_evidence_tokens: 2200

## EVIDENCE

- `control/inventory/public_alpha_reassess_06_result.json`
- `control/inventory/public_alpha_reassess_06_validation_matrix.json`
- `control/audits/public-alpha-reassess-06-v0/`
- `examples/public_alpha/reassess/review_batch_apply/`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-06/README.md`

## NEXT

`INDEXLESS-LIVE-SEARCH-FALLBACK-00 - Add live metadata fallback when indexes are unavailable`
