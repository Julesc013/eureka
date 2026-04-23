## Bounded Action Routing

`runtime/engine/action_routing/` holds the first bounded action-routing and recommendation seam for Eureka.

This slice is intentionally small. It takes:

- one already resolved target
- bounded representation and access-path summaries
- an optional bounded host profile compatibility verdict
- an optional bounded strategy profile
- bounded local export/store availability context

and returns a compact ordered action plan with:

- `recommended` actions
- `available` actions
- `unavailable` actions plus explicit reasons

This is not:

- an execution engine
- an installer
- a runtime launcher
- a restore/import workflow
- a final policy engine

The current rules are bootstrap-scale and replaceable. They exist to prove that Eureka can surface explicit next-step guidance without silently hiding blocked or unavailable actions.

The current strategy seam is also bounded and explicit:

- `inspect` emphasizes source inspection and evidence-aware review
- `preserve` emphasizes deterministic export and local store actions
- `acquire` emphasizes direct bounded access paths when compatibility allows it
- `compare` emphasizes subject-state and side-by-side review paths when meaningful

These strategy profiles do not mutate the underlying resolved identity,
evidence, or representation truth. They only change bounded recommendation
emphasis.
