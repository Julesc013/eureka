# AIDE Latest Task Packet

## PHASE

AIDE-BATCH-LOCAL-APPLY-GATE-01

## GOAL

Add the explicit local operator apply gate for approved reviewed-index refreshes.
The gate must keep dry-run as default and require an explicit outside-repo
instance path, operator token, exact confirmation string, backup, mutation
manifest, audit log, post-apply validation, rollback plan, and rollback proof.

## WHY

Workbench review/promote already proves candidate-to-reviewed-index behavior in
temp scope. LOCAL-APPLY-GATE-01 turns that proof into a reusable local mutation
protocol without silently touching the operator instance or claiming production
readiness.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/queue/AIDE-BATCH-LOCAL-APPLY-GATE-01/task.yaml`
- `.aide/queue/LOCAL-APPLY-GATE-01/task.yaml`
- `control/inventory/workbench_review_promote_result.json`
- `control/inventory/local_apply_gate_input_state.json`
- `control/inventory/local_apply_gate_result.json`
- `control/audits/local-apply-gate-01-v0/README.md`

## ALLOWED_PATHS

- `contracts/local_apply/**`
- `contracts/instances/**`
- `runtime/local/apply/**`
- `runtime/local/service/**`
- `scripts/eureka_local_apply.py`
- `scripts/eureka_local_apply_backup.py`
- `scripts/eureka_local_apply_rollback.py`
- `scripts/validate_local_apply_gate.py`
- `tools/generators/eureka_local_apply*.py`
- `tools/validators/validate_local_apply_gate.py`
- `tests/runtime/test_local_apply*.py`
- `tests/operations/test_local_apply*.py`
- `tests/scripts/test_validate_local_apply_gate.py`
- `examples/local_apply/**`
- `control/policies/local_apply*.json`
- `control/policies/operator_instance_mutation_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/local_apply*.json`
- `docs/architecture/LOCAL_APPLY*.md`
- `docs/architecture/OPERATOR_INSTANCE_MUTATION_MODEL.md`
- `docs/operations/LOCAL_APPLY*.md`
- `docs/operations/POST_LOCAL_APPLY_GATE_PLAN.md`
- `docs/reference/LOCAL_APPLY*.md`
- `.aide/queue/AIDE-BATCH-LOCAL-APPLY-GATE-01/**`
- `.aide/queue/LOCAL-APPLY-GATE-01/**`
- `.aide/queue/WORKBENCH-LOCAL-LOOP-CLOSEOUT-01/**`
- `.aide/queue/SOURCE-ACTION-KERNEL-00/**`
- `.aide/queue/SOURCE-WAVE-00/**`
- `.aide/queue/SNAPSHOT-RELAY-00/**`
- `.aide/queue/PUBLIC-ALPHA-READONLY-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/local-apply-gate-01-v0/**`
- `tools/generators/local_queue_progress.py`
- `tools/validators/check_generated_artifact_cleanliness.py`
- `tools/validators/validate_local_appliance_track.py`

## FORBIDDEN_PATHS

- no `instances/**` or committed operator instance state
- no `.aide.local/**`, secrets, `.env`, raw prompts, raw responses, raw live source responses
- no `site/dist/**` or `data/public_index/**` mutation
- no master index mutation
- no downloads, uploads, extraction, execution, model/provider calls, deployment
- no production readiness or public launch readiness claim

## IMPLEMENTATION

- add governed local apply contracts and instance mutation contracts
- add explicit local apply, backup, audit, manifest, validation, and rollback runtime helpers
- add thin script wrappers and tool implementations for apply, backup, rollback, and validation
- add API route reservations that keep mutations behind the CLI gate
- add deterministic examples, docs, policies, matrices, result inventory, queue status, and audit evidence

## VALIDATION

- `python scripts/validate_local_apply_gate.py`
- focused local apply runtime/script/validator tests
- boundary checks, generated artifact cleanliness, repo structure and contract validators
- selected lane router during development
- full discovery at final closeout if practical; otherwise record exact deferral

## EVIDENCE

- `control/inventory/local_apply_gate_input_state.json`
- `control/inventory/local_apply_smoke_result.json`
- `control/inventory/local_apply_validation_matrix.json`
- `control/inventory/local_apply_gate_result.json`
- `control/audits/local-apply-gate-01-v0/`

## NON_GOALS

- no public hosted behavior
- no SOURCE-WAVE implementation
- no SNAPSHOT-RELAY implementation
- no native client implementation
- no source probe, download, upload, extraction, execution, install, model/provider call, deployment, production claim, or public launch claim

## ACCEPTANCE

- dry-run preview passes
- apply without token is blocked
- apply without confirmation is blocked
- repo path target is blocked
- temp explicit instance apply passes
- backup, mutation manifest, audit log, rollback plan, post-apply validation, rollback, and post-rollback validation pass
- public and native read-only projections remain blocked
- no committed instance state or master/public index mutation occurs

## OUTPUT_SCHEMA

- `local_apply_gate_result.v0`
- `local_apply_validation_matrix.v0`
- `local_apply_gate_smoke_result.v0`

## TOKEN_ESTIMATE

- task packet target: under 1600 approximate tokens
- review packet generated by `aide_lite.py review-pack`
