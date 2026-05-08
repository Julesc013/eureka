# TRACK-B-02 - Node Policy Contract

This audit pack records the Track B node policy milestone.

## Added

- `contracts/node/node_policy.v0.json` defines the node policy envelope.
- Node policy, action, source access, output, and review-gate registries live under `control/inventory/nodes/`.
- Seven example policies cover local, future, and blocked node policy postures.
- `scripts/validate_eureka_node_policy.py` and `tests/contracts/test_eureka_node_policy.py` validate the policy boundary.

## Why This Follows The Manifest

TRACK-B-01 defined node identity. TRACK-B-02 defines the policy envelope that constrains future node behavior before any node runtime, WorkUnit runtime, local state, or source access can be implemented.

## Boundaries Preserved

- No node runtime was implemented.
- No local state was created.
- No network, browser, API, model, or provider access was enabled.
- No observations were performed or marked observed.
- No evidence, candidate, observation, pack, or node output was accepted as public truth.
- No master index mutation path was enabled.

## Validation

Run:

```text
python -m json.tool control/inventory/nodes/node_policy_registry.json
python -m json.tool control/inventory/nodes/node_action_policy.json
python -m json.tool control/inventory/nodes/node_source_access_policy.json
python -m json.tool control/inventory/nodes/node_output_policy.json
python -m json.tool control/inventory/nodes/node_review_gate_policy.json
python -m json.tool control/audits/track-b-02-node-policy-contract-v0/track_b_02_report.json
python scripts/validate_eureka_node_manifest.py
python scripts/validate_eureka_node_policy.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## Deferred

TRACK-B-03 will define the node capability contract. Node runtime, local state, source access execution, WorkUnit execution, pack import/export, review runtime, hosted behavior, and master-index promotion remain future review-gated work.
