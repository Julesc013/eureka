# Node Policy Evaluation Review

Node policy evaluations are reviewable reports. Reviewers use them to decide
whether a WorkUnit can be validated, simulated, deferred, blocked, or sent back
for policy/capability changes.

## Review Rules

- Treat every evaluation as a planning signal, not public truth.
- Do not treat `allowed_for_dry_run` as execution approval.
- Require review before downstream WorkUnit dry-run use.
- Require separate future review before any network, model, source-access,
  local-state, public-export, or master-index scope is enabled.
- Preserve all false truth and product boundary booleans.

## Blockers

Block the evaluation when it includes:

- unknown required capabilities
- forbidden inputs, outputs, or actions
- required network access while network remains disabled
- required model/provider access while providers remain disabled
- required credentials
- required local private state while local state remains disabled
- source access outside approved policy
- accepted evidence, accepted public record, or master-index mutation claims
- rights, malware-safety, installability, exhaustive-search, or
  production-readiness claims

## Gated And Deferred Cases

Future metadata probe and source-policy workflows may be represented as
`approval_gated`, `operator_gated`, `permission_needed`, or `deferred_future`.
Those decisions preserve the future intent without activating source access,
network calls, or node runtime behavior.

## Validation Commands

Run the evaluator and validator:

```bash
python scripts/evaluate_node_policy.py --node-manifest examples/nodes/local_private_node_v0/eureka_node_manifest.json --node-policy examples/nodes/policies/local_private_node_policy_v0.json --workunit examples/work_units/search_need_review_v0/work_unit.json --check
python scripts/validate_node_policy_evaluator.py
```

Full Track B validation also runs existing node, WorkUnit, WorkUnit result,
local foundry state, query observation, search miss, SearchNeed, dry-run, unit
test, and architecture-boundary checks.

