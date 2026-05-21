# AIDE Latest Task Packet

## PHASE

AIDE-BATCH-F0-FOUNDATION-01

## GOAL

Add the F0 extraction/member discovery policy and safe fixture foundation so Eureka can enumerate tiny committed fixture manifests and seed future review-gated WorkUnits without enabling broad extraction.

## WHY

F0 creates the boundary layer needed before later member discovery, extraction policy, ranking, source-wave, and snapshot relay work. The foundation must prove that archive/member inspection remains fixture-only, manifest-only, candidate-only, and blocked by default.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/AIDE-BATCH-F0-FOUNDATION-01/task.yaml`
- `.aide/queue/F0-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/f0_foundation_result.json`
- `control/audits/f0-foundation-01-v0/`
- `docs/architecture/F0_EXTRACTION_MEMBER_DISCOVERY.md`
- `scripts/validate_f0_foundation.py`

## ALLOWED_PATHS

- `.aide/queue/AIDE-BATCH-F0-FOUNDATION-01/**`
- `.aide/queue/F0-00/task.yaml`
- `.aide/queue/G0/task.yaml`
- `.aide/queue/SOURCE-WAVE-00/task.yaml`
- `.aide/queue/SNAPSHOT-RELAY-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/extraction/**`
- `contracts/workunits/**`
- `contracts/domain/**`
- `contracts/scout/**`
- `contracts/syn/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `runtime/local_eval/**`
- `runtime/local_workbench/**`
- `runtime/local_service/**`
- `runtime/workunit_queue/**`
- `runtime/search_need/**`
- `runtime/search_hunt/**`
- `runtime/extraction_safe_fixtures/**`
- `examples/extraction/**`
- `examples/f0/**`
- `examples/domain/**`
- `examples/scout/**`
- `examples/syn/**`
- `examples/ia_hunt_bridge/**`
- `examples/workbench/result_lanes/**`
- `evals/extraction/**`
- `evals/f0/**`
- `evals/domain/**`
- `evals/scout/**`
- `evals/syn/**`
- `scripts/eureka_f0_manifest.py`
- `scripts/eureka_f0_fixture_builder.py`
- `scripts/eureka_f0_workunit_seed.py`
- `scripts/eureka_f0_smoke.py`
- `scripts/validate_f0_foundation.py`
- `scripts/audit_hunt_main_promotion.py`
- `scripts/hunt_queue_progress.py`
- `scripts/local_queue_progress.py`
- `scripts/validate_contract_taxonomy_plan.py`
- `scripts/validate_hunt_main_promotion.py`
- `scripts/validate_hunt_remediation.py`
- `scripts/validate_hunt_remediation_continue.py`
- `scripts/validate_local_appliance_track.py`
- `scripts/validate_search_hunt_closeout.py`
- `scripts/validate_scout_schema.py`
- `scripts/validate_domain_packs.py`
- `scripts/validate_syn_foundry.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_f0_foundation.py`
- `tests/runtime/test_f0_safe_fixture_manifest.py`
- `tests/runtime/test_f0_member_manifest.py`
- `tests/runtime/test_f0_resource_policy.py`
- `tests/runtime/test_f0_workunit_seed.py`
- `tests/operations/test_f0_scripts.py`
- `tests/operations/test_f0_smoke.py`
- `tests/operations/test_search_hunt_track.py`
- `tests/scripts/test_validate_f0_foundation.py`
- `control/policies/f0_extraction_policy.json`
- `control/policies/f0_fixture_policy.json`
- `control/policies/f0_resource_limit_policy.json`
- `control/policies/f0_member_manifest_policy.json`
- `control/policies/f0_non_claim_policy.json`
- `control/policies/f0_future_fetch_policy.json`
- `control/policies/f0_future_ai_policy.json`
- `control/inventory/f0_*.json`
- `docs/architecture/F0_*.md`
- `docs/operations/F0_FOUNDATION_RUNBOOK.md`
- `docs/operations/POST_F0_FOUNDATION_PLAN.md`
- `docs/reference/F0_*.md`
- `control/audits/f0-foundation-01-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`
- private local files
- committed operator tokens
- committed provider credentials
- raw prompts
- raw responses
- raw live IA response bodies

## IMPLEMENTATION

- Added F0 policies, contracts, matrices, examples, docs, and audit evidence.
- Added `runtime/extraction_safe_fixtures/` with read-only fixture helpers.
- Added F0 CLIs and validator.
- Added focused runtime, operation, smoke, and validator tests.
- Kept unsafe/pathological fixtures as descriptors rather than dangerous archives.

## VALIDATION

- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/validate_f0_foundation.py`
- `python scripts/validate_scout_schema.py`
- `python scripts/validate_domain_packs.py`
- `python scripts/validate_syn_foundry.py`
- `python scripts/validate_ia_hunt_bridge.py`
- `python scripts/validate_workbench_result_lanes.py`
- `python scripts/validate_search_interaction_contract.py`
- `python scripts/validate_workbench_foundation.py`
- `python scripts/validate_test_lane_policy.py`
- `python scripts/validate_contract_taxonomy.py`
- `python scripts/validate_repo_structure_canon.py`
- `python -m unittest tests.runtime.test_f0_foundation`
- `python -m unittest tests.runtime.test_f0_safe_fixture_manifest`
- `python -m unittest tests.runtime.test_f0_member_manifest`
- `python -m unittest tests.runtime.test_f0_resource_policy`
- `python -m unittest tests.runtime.test_f0_workunit_seed`
- `python -m unittest tests.operations.test_f0_scripts`
- `python -m unittest tests.operations.test_f0_smoke`
- `python -m unittest tests.scripts.test_validate_f0_foundation`
- `python scripts/check_architecture_boundaries.py`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`
- `python -m unittest discover -s tests -t .`
- `git diff --check`

## COMMITS

- Planned: `feat(f0): add extraction member discovery foundation`

## EVIDENCE

- `control/inventory/f0_validation_matrix.json`
- `control/inventory/f0_foundation_result.json`
- `control/audits/f0-foundation-01-v0/f0_foundation_report.json`
- `control/audits/f0-foundation-01-v0/generated/`

## NON_GOALS

- no live source calls
- no source probes
- no downloads/uploads
- no filesystem extraction
- no arbitrary file extraction
- no execution/install/emulation
- no model/provider calls
- no public fanout
- no operator instance mutation
- no master/public index mutation
- no fake evidence
- no fake verified records
- no production readiness claim
- no public launch readiness claim
- no broad extraction runtime
- no G0 ranking implementation
- no source expansion implementation

## ACCEPTANCE

- F0 contracts, policies, matrices, fixtures, runtime helpers, scripts, tests, docs, audit pack, and queue metadata are present.
- Safe ZIP manifest enumeration passes.
- Unsafe descriptor blocks pass.
- WorkUnit seed output is dry-run only.
- Operator, public, and native read-only smoke projections pass.
- Cross-stack validators pass.
- Full unittest discovery passes if practical.
- Working tree is clean after commit.

## OUTPUT_SCHEMA

Return final report with `STATUS`, `SUMMARY`, `COMMITS`, `F0_FOUNDATION`, `VALIDATION`, `PUSH`, `BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1800
- budget_status: PASS
- warnings:
  - none
