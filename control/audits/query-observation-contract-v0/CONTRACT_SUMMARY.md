# Contract Summary

P59 adds `contracts/query/query_observation.v0.json` and the
`control/inventory/query_intelligence/query_observation_policy.json` inventory.

The contract captures:

- normalized query terms and a non-reversible fingerprint
- coarse intent, destination, and detected public-safe entities
- summary-only result posture
- checked index/source scope
- privacy and retention policy
- probe policy with enqueueing disabled
- hard no-mutation guarantees

It is contract-only. No runtime query collection or telemetry exists.
