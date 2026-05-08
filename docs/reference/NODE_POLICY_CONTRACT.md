# Node Policy Contract

`contracts/node/node_policy.v0.json` defines the policy envelope for future Eureka Nodes.

A node manifest identifies a node. A node policy constrains that node: what committed inputs it may read, what proposed outputs it may prepare, what source access modes it may request, which review gates apply, and which actions remain forbidden.

## Boundaries

- A node policy is not a node runtime.
- A node policy does not permit live probes, arbitrary URL fetches, scraping, crawling, downloads, uploads, accounts, telemetry, or provider/model calls.
- A node policy does not permit accepted evidence truth, accepted public records, observed baseline truth, or master index mutation.
- Any future widening of autonomy requires explicit policy, source access review, operator approval, and audit evidence.

## Required Policy Areas

Policies define input, action, source access, network, local state, output, review gate, pack, evidence, candidate, observation, WorkUnit, budget, audit, privacy, rights, and risk boundaries.

The current contract requires `network_policy.network_enabled` and `local_state_policy.local_state_enabled` to remain false for examples. It also requires output truth booleans to remain false.

## Validation

Run:

```text
python scripts/validate_eureka_node_policy.py
python -m unittest tests.contracts.test_eureka_node_policy
```

## Deferred

TRACK-B-03 will define the node capability contract. Runtime, local state, source access execution, WorkUnit execution, and master-index promotion remain later review-gated work.
