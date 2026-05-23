# TRACK-B-03 - Node Capability Contract

This audit pack records the Track B node capability milestone.

## Added

- `contracts/schema/control/policies/node/node_capability.v0.json` defines declarative capability records.
- Capability policy, matrix, dependency, and side-effect inventories live under `control/inventory/nodes/`.
- Six example capability records cover current repo-local, dry-run, validate-only, future source/model, and blocked postures.
- `scripts/validate_eureka_node_capability.py` and `tests/contracts/test_eureka_node_capability.py` validate the capability boundary.

## Why This Follows Manifests And Policies

TRACK-B-01 defined node identity. TRACK-B-02 defined the policy envelope. TRACK-B-03 defines what capabilities may be named under those boundaries before WorkUnit contracts introduce executable units of work.

## Boundaries Preserved

- No node runtime was implemented.
- No WorkUnit runtime was implemented.
- No local state was created.
- No network, browser, API, model, or provider access was enabled.
- No observations were performed or marked observed.
- No evidence, candidate, observation, pack, capability, or node output was accepted as public truth.
- No master index mutation path was enabled.

## Validation

Run:

```text
python -m json.tool control/inventory/nodes/node_capability_policy.json
python -m json.tool control/inventory/nodes/node_capability_matrix.json
python -m json.tool control/inventory/nodes/node_capability_dependency_policy.json
python -m json.tool control/inventory/nodes/node_capability_side_effect_policy.json
python -m json.tool control/audits/track-b-03-node-capability-contract-v0/track_b_03_report.json
python scripts/validate_eureka_node_manifest.py
python scripts/validate_eureka_node_policy.py
python scripts/validate_eureka_node_capability.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## Deferred

TRACK-B-04 will define WorkUnit contracts. Runtime execution, local state, source access, model/provider access, hosted workers, pack import/export, review runtime, and master-index promotion remain future review-gated work.
