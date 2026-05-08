# WorkUnit Model

WorkUnits sit after node manifests, node policies, and node capabilities.
Manifests identify a node, policies constrain behavior, capabilities describe
designed powers, and WorkUnits describe bounded replay-safe work under those
constraints.

## Model

Each WorkUnit records:

- identity: `workunit_id`, type, status, scope, priority
- node requirements: modes, manifests, capabilities, and policies
- input/output policy: allowed committed inputs and reviewable outputs
- action policy: allowed local/review actions and forbidden unsafe actions
- source/runtime requirements: source, network, model, credential, and local
  state requirements with current enablement false
- idempotency: rerun, duplicate, recovery, and stop-condition behavior
- review gates: human, source-policy, evidence, candidate, pack,
  master-index, rights, risk, privacy, and operator gates
- truth boundary: WorkUnit results are not accepted truth

## Replay Safety

The WorkUnit model is intentionally resumable. If a task is repeated, stale,
partial, out of order, or conflicting, the policy says to validate, resume only
missing acceptance work, quarantine conflicts, or record a blocker. Destructive
ambiguity, private data exposure risk, unsafe source/network actions, legal or
licensing questions, and deployment/hosting mutations are stop conditions.

## Future Runtime

This contract prepares future WorkUnit result and runner planning. It does not
create a runner, execute a task, create local state, or widen any runtime
surface.
