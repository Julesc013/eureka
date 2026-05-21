# AIDE Latest Task Packet

## PHASE

AIDE-BATCH-SCOUT-SCHEMA-01 - SCOUT discovery trail, relation, source trust, and WorkUnit seed contracts

## GOAL

Define the SCOUT schema foundation: candidate-only discovery seeds, relation
types, discovery candidates, trails, source trust records/observations, feedback
events, WorkUnit seed suggestions, DOMAIN/SYN handoff matrices, read-only console
view models, validator, tests, docs, and audit evidence.

## WHY

SCOUT gives Eureka a governed relation/path discovery vocabulary without turning
relations into accepted truth. The batch prepares later F0/G0/source work while
preserving review gates and keeping live source behavior, crawling, extraction,
model calls, and index mutation disabled.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/AIDE-BATCH-SCOUT-SCHEMA-01/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/domain_foundation_result.json`
- `runtime/local_eval/domain_packs.py`

## ALLOWED_PATHS

- `contracts/scout/**`
- `contracts/domain/**`
- `contracts/syn/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `runtime/local_eval/**`
- `runtime/local_workbench/**`
- `runtime/local_service/**`
- `examples/scout/**`
- `examples/domain/**`
- `examples/syn/**`
- `examples/ia_hunt_bridge/**`
- `examples/workbench/result_lanes/**`
- `evals/scout/**`
- `evals/domain/**`
- `evals/syn/**`
- `scripts/eureka_scout_schema.py`
- `scripts/eureka_scout_console.py`
- `scripts/validate_scout_schema.py`
- `scripts/validate_domain_packs.py`
- `scripts/validate_syn_foundry.py`
- `scripts/eureka_test_select.py`
- `scripts/validate_hunt_remediation.py`
- `scripts/validate_hunt_remediation_continue.py`
- `scripts/validate_search_hunt_closeout.py`
- `tests/runtime/test_scout_schema.py`
- `tests/runtime/test_scout_relations.py`
- `tests/runtime/test_scout_domain_syn_handoff.py`
- `tests/operations/test_scout_schema_scripts.py`
- `tests/operations/test_scout_console.py`
- `tests/operations/test_search_hunt_track.py`
- `tests/scripts/test_validate_scout_schema.py`
- `control/policies/scout_schema_policy.json`
- `control/policies/scout_non_claim_policy.json`
- `control/policies/scout_relation_policy.json`
- `control/policies/scout_source_trust_policy.json`
- `control/policies/scout_feedback_policy.json`
- `control/policies/scout_future_ai_policy.json`
- `control/inventory/scout_schema_input_state.json`
- `control/inventory/scout_contract_matrix.json`
- `control/inventory/scout_relation_type_matrix.json`
- `control/inventory/scout_seed_inventory.json`
- `control/inventory/scout_discovery_candidate_matrix.json`
- `control/inventory/scout_discovery_trail_matrix.json`
- `control/inventory/scout_source_trust_matrix.json`
- `control/inventory/scout_feedback_event_matrix.json`
- `control/inventory/scout_workunit_seed_matrix.json`
- `control/inventory/scout_domain_handoff_matrix.json`
- `control/inventory/scout_syn_handoff_matrix.json`
- `control/inventory/scout_workbench_console_matrix.json`
- `control/inventory/scout_failure_repair_log.json`
- `control/inventory/scout_validation_matrix.json`
- `control/inventory/scout_schema_result.json`
- `control/inventory/scout_schema_next_task_decision.json`
- `control/inventory/contract_migration_plan.json`
- `control/inventory/contract_reference_graph.json`
- `control/inventory/contract_risk_register.json`
- `control/inventory/contract_taxonomy_inventory.json`
- `control/inventory/r0_03b_execution_plan.json`
- `docs/architecture/SCOUT_CURATOR_GRAPH.md`
- `docs/architecture/SCOUT_DISCOVERY_TRAILS.md`
- `docs/architecture/SCOUT_SOURCE_TRUST.md`
- `docs/operations/SCOUT_SCHEMA_RUNBOOK.md`
- `docs/operations/POST_SCOUT_SCHEMA_PLAN.md`
- `docs/reference/SCOUT_DISCOVERY_CANDIDATE.md`
- `docs/reference/SCOUT_DISCOVERY_TRAIL.md`
- `docs/reference/SCOUT_SOURCE_TRUST_RECORD.md`
- `docs/reference/SCOUT_RELATION_TYPES.md`
- `.aide/queue/AIDE-BATCH-SCOUT-SCHEMA-01/**`
- `.aide/queue/SCOUT-SCHEMA-00/task.yaml`
- `.aide/queue/F0-00/task.yaml`
- `.aide/queue/G0/task.yaml`
- `.aide/queue/SOURCE-WAVE-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/scout-schema-01-v0/**`
- `control/audits/r0-03a-contract-taxonomy-refactor-plan-v0/**`

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

## IMPLEMENTATION

- Keep SCOUT read-only and candidate-only.
- Do not implement crawling, live relation walking, extraction, model calls, or index mutation.
- Use selected tests during development and full discovery at closeout if practical.
- Record repairable metadata/test failures in `control/inventory/scout_failure_repair_log.json`.

## VALIDATION

- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/validate_scout_schema.py`
- focused SCOUT tests
- neighboring foundation validators
- AIDE checks
- full discovery if practical

## COMMITS

- Commit `feat(scout): add discovery schema foundation` with structured body.
- Push `dev` if the remote dev branch has not advanced.
- Do not push `main`.

## EVIDENCE

- `control/audits/scout-schema-01-v0/`
- `control/inventory/scout_validation_matrix.json`
- `control/inventory/scout_schema_result.json`
- `control/inventory/scout_schema_next_task_decision.json`
- `.aide/context/latest-review-packet.md`

## NON_GOALS

- No live source calls, source probes, crawling, downloads/uploads, extraction,
  model/provider calls, public fanout, operator instance mutation, master/public
  index mutation, fake evidence, fake verified records, deployment, production
  readiness claim, or public launch claim.

## ACCEPTANCE

- SCOUT contracts/examples/matrices/docs/tests validate.
- SCOUT remains read-only, candidate-only, no live source call, no crawling, no
  fake evidence, and review-gated.

## OUTPUT_SCHEMA

Return STATUS, SUMMARY, COMMITS, SCOUT_SCHEMA, VALIDATION, PUSH, BOUNDARIES, and NEXT_TASK.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 7600
- approx_tokens: 1900
- budget_status: PASS
