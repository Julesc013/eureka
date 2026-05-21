# AIDE Latest Task Packet

## PHASE

AIDE-BATCH-G0-QUALITY-FOUNDATION-01

## GOAL

Add deterministic fixture-only G0 foundations for ranking, explanation,
identity grouping, near misses, user-cost/actionability scoring, and a read-only
Workbench quality console model.

## WHY

G0 gives Eureka transparent quality packets over Local/HUNT/PLAY/IA/Workbench,
SYN, DOMAIN, SCOUT, and F0 records without creating truth, changing public
ranking, accepting identity merges, or mutating indexes.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/AIDE-BATCH-G0-QUALITY-FOUNDATION-01/task.yaml`
- `.aide/queue/G0/task.yaml`
- `.aide/queue/index.yaml`
- `control/inventory/g0_foundation_result.json`
- `control/audits/g0-quality-foundation-01-v0/`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `docs/architecture/G0_RANKING_EXPLANATION_QUALITY.md`
- `runtime/local_eval/g0_quality.py`
- `scripts/validate_g0_foundation.py`

## ALLOWED_PATHS

- `.aide/queue/AIDE-BATCH-G0-QUALITY-FOUNDATION-01/**`
- `.aide/queue/G0/task.yaml`
- `.aide/queue/SOURCE-WAVE-00/task.yaml`
- `.aide/queue/SNAPSHOT-RELAY-00/task.yaml`
- `.aide/queue/WORKBENCH-QUALITY-CONSOLE-01/task.yaml`
- `.aide/queue/WORKBENCH-QUALITY-CONSOLE-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/search_quality/**`
- `contracts/ranking/**`
- `contracts/explanation/**`
- `contracts/identity/**`
- `contracts/user_cost/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/domain/**`
- `contracts/scout/**`
- `contracts/syn/**`
- `contracts/extraction/**`
- `runtime/local_eval/**`
- `runtime/local_workbench/**`
- `runtime/local_service/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/public_index/**`
- `runtime/candidate_index/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/review_queue/**`
- `runtime/extraction_safe_fixtures/**`
- `examples/search_quality/**`
- `examples/ranking/**`
- `examples/explanation/**`
- `examples/identity/**`
- `examples/user_cost/**`
- `examples/f0/**`
- `examples/scout/**`
- `examples/domain/**`
- `examples/syn/**`
- `examples/ia_hunt_bridge/**`
- `examples/workbench/result_lanes/**`
- `evals/search_quality/**`
- `evals/ranking/**`
- `evals/explanation/**`
- `evals/identity/**`
- `evals/user_cost/**`
- `evals/f0/**`
- `evals/scout/**`
- `evals/domain/**`
- `evals/syn/**`
- `scripts/eureka_g0_*.py`
- `scripts/validate_g0_foundation.py`
- `scripts/validate_f0_foundation.py`
- `scripts/validate_scout_schema.py`
- `scripts/validate_domain_packs.py`
- `scripts/validate_syn_foundry.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_g0_*.py`
- `tests/operations/test_g0_*.py`
- `tests/operations/test_search_hunt_track.py`
- `tests/scripts/test_validate_g0_foundation.py`
- `control/policies/g0_*.json`
- `control/inventory/g0_*.json`
- `docs/architecture/G0_*.md`
- `docs/operations/G0_FOUNDATION_RUNBOOK.md`
- `docs/operations/POST_G0_FOUNDATION_PLAN.md`
- `docs/reference/G0_*.md`
- `control/audits/g0-quality-foundation-01-v0/**`

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
- `native/**`
- `crates/**`
- private local files
- committed operator tokens
- committed provider credentials
- raw prompts
- raw responses
- raw live IA response bodies

## NON_GOALS

- No production ranking engine.
- No accepted identity merge.
- No evidence or reviewed-record creation.
- No live source calls, source probes, downloads, extraction, execution, model/provider calls, or deployment.
- No operator instance, public index, or master index mutation.
- No production readiness or public launch claim.

## IMPLEMENTATION

- Added G0 policies, contracts, matrices, examples, docs, and audit evidence.
- Added `runtime/local_eval/g0_quality.py` with read-only deterministic helpers.
- Added G0 CLIs and validator.
- Added focused runtime, operation, smoke, and validator tests.

## ACCEPTANCE

- G0 contracts, policies, matrices, examples, docs, scripts, and tests are present.
- Score breakdowns, explanation packets, provisional identity clusters, near misses, and user-cost scores validate.
- Operator, public, and native read-only console projections pass smoke checks.
- Full unittest discovery passes for closeout.
- Boundary flags remain false for fake evidence, fake verified records, accepted identity merge, source probes, live calls, downloads, extraction, model/provider calls, index mutation, deployment, and production/public launch claims.

## VALIDATION

- `python scripts/validate_g0_foundation.py`
- G0 focused tests
- selected test lane router
- global validators
- full discovery at closeout when practical

## OUTPUT_SCHEMA

- Result: `control/inventory/g0_foundation_result.json`
- Validation matrix: `control/inventory/g0_validation_matrix.json`
- Next task decision: `control/inventory/g0_foundation_next_task_decision.json`
- Audit report: `control/audits/g0-quality-foundation-01-v0/g0_foundation_report.json`

## TOKEN_ESTIMATE

- Latest task packet: compact handoff-sized packet, under AIDE Lite validation budget.
- Latest review packet: generated by `python .aide/scripts/aide_lite.py review-pack`.

## COMMITS

- Planned: `feat(g0): add quality explanation foundation`

## EVIDENCE

- `control/inventory/g0_validation_matrix.json`
- `control/inventory/g0_foundation_result.json`
- `control/audits/g0-quality-foundation-01-v0/g0_foundation_report.json`
- `control/audits/g0-quality-foundation-01-v0/generated/`
