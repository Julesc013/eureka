# Node Policy Evaluation: node_policy_eval_a0b4606774f4

- Status: warn
- Decision: allowed_for_dry_run
- Node manifest: examples/nodes/local_private_node_v0/eureka_node_manifest.json
- Node policy: examples/nodes/policies/local_private_node_policy_v0.json
- WorkUnit: examples/work_units/search_need_review_v0/work_unit.json
- Allowed for dry-run: true
- Allowed for execution: false
- Allowed for master-index mutation: false

## Warnings
- action prepare_search_need_seed_future is future/deferred and simulated only
- capability search_need_analysis is registry-allowed but not declared by manifest
