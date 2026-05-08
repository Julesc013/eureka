# Node Policy Evaluator

The Node Policy Evaluator is a local, explicit-input policy checker for Eureka
node planning. It reads a node manifest, node policy, capability registry, and a
WorkUnit JSON file, then emits a `node_policy_evaluation_result.v0` report.

The evaluator answers whether the WorkUnit can be validated, simulated by the
dry-run runner, blocked, deferred, operator-gated, human-operated, or
approval-gated for the selected node.

## What It Is Not

The evaluator is not a WorkUnit executor and not a node runtime. It does not
perform observations, access sources, call networks, call APIs, call models or
providers, create local private state, accept evidence, accept candidates, or
mutate the master index.

## Inputs

Current input roots are committed examples and policy inventories:

- `examples/nodes/`
- `examples/work_units/`
- `examples/work_unit_results/`
- `control/inventory/nodes/`
- `control/audits/**/generated/`
- explicit temporary test directories

Forbidden inputs include product build output, runtime-generated reports,
contract output locations, publication inventories, master-index roots, local
private roots, secrets, credentials, account sessions, telemetry streams, and
unreviewed live-source payloads.

## Decisions

Decision values are governed by
`control/inventory/nodes/node_policy_evaluation_decision_registry.json`.

Allowed current decisions include:

- `allowed_for_dry_run`
- `allowed_for_validation`
- `allowed_for_report_only`
- `allowed_for_manual_review`
- `allowed_as_noop`
- `blocked_by_policy`
- `blocked_by_missing_policy`
- `blocked_by_unknown_capability`
- `blocked_by_source_access`
- `blocked_by_network_requirement`
- `blocked_by_model_requirement`
- `blocked_by_credential_requirement`
- `blocked_by_local_state_requirement`
- `blocked_by_forbidden_input`
- `blocked_by_forbidden_output`
- `blocked_by_forbidden_action`
- `operator_gated`
- `human_operated`
- `approval_gated`
- `permission_needed`
- `deferred_future`
- `not_evaluable`

Allowed decisions authorize report or dry-run preparation only. They never
authorize WorkUnit execution.

## Reasons

Reason categories are governed by
`control/inventory/nodes/node_policy_evaluation_reason_registry.json`. Reasons
explain how the decision was reached, including node mode scope, capability
coverage, input/output/action policy, source access, network/model/credential
requirements, local-state requirements, and review gates.

## Output

The evaluator writes no files by default. With `--output`, it may write an
explicit evaluation report under:

- `control/audits/**/generated/`
- `examples/node_policy_evaluations/**/evaluation_result.json`
- an explicit temporary test directory

It refuses product runtime, contract, publication, master-index, and local
private roots.

## Truth Boundary

Every evaluation result preserves:

- `evaluation_result_is_public_truth: false`
- `evaluation_result_is_accepted_evidence: false`
- `evaluation_result_can_mutate_master_index: false`
- rights, malware-safety, installability, exhaustive-search, and production
  claims as false
- `human_review_required_for_downstream_use: true`

## Validation

Use:

```bash
python scripts/evaluate_node_policy.py --node-manifest examples/nodes/local_private_node_v0/eureka_node_manifest.json --node-policy examples/nodes/policies/local_private_node_policy_v0.json --workunit examples/work_units/search_need_review_v0/work_unit.json --check
python scripts/validate_node_policy_evaluator.py
```

