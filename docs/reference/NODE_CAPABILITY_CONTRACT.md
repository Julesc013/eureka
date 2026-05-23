# Node Capability Contract

`contracts/schema/control/policies/node/node_capability.v0.json` defines a declarative capability record for future Eureka Nodes.

Manifests identify nodes. Policies constrain behavior. Capabilities describe what a node may be designed to do under those policies. A capability is not runtime permission, source approval, model/provider approval, network approval, or master index authority.

## Current And Future Capabilities

Current capabilities are limited to contract-only, repo-local, validation-only, or dry-run-only work. They operate on committed public-safe inputs and preserve false network, source, model/provider, credential, and local-state requirement flags.

Future capabilities may be declared when they are marked future, deferred, approval-gated, operator-gated, human-operated, or blocked. They must keep current enabled flags false and require review gates, source policy, operator approval, kill switches, and budget/rate policy where relevant.

## Boundaries

Every capability must keep truth-boundary booleans false for observed baselines, accepted evidence, public truth, master index mutation, rights clearance, malware safety, verified installability, and exhaustive search claims.

Capability examples must not contain credentials, private paths, API keys, live-source results, scraped content, telemetry, account/session data, downloads, active runtime claims, active model/provider claims, or production-readiness claims.

## Validation

Run:

```text
python scripts/validate_eureka_node_capability.py
python -m unittest tests.contracts.test_eureka_node_capability
```

## Deferred

TRACK-B-04 will define WorkUnit contracts. Runtime execution, source access, local state, model/provider use, hosted workers, and promotion workflows remain future review-gated work.
