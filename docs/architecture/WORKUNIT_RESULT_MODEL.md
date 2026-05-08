# WorkUnit Result Model

WorkUnit results follow WorkUnit contracts. A WorkUnit describes bounded work;
a WorkUnit result describes the outcome envelope for that work without
implementing a runner.

## Envelope

The result model records:

- source WorkUnit, node manifest, node policy, and capability refs
- execution mode and execution summary
- validation summary
- planned, executed, skipped, blocked, and forbidden-checked actions
- observed inputs and proposed or rejected outputs
- noop, duplicate, resume, recovery, out-of-order, and quarantine posture
- review gates and truth boundaries

## Replay Posture

Repeated WorkUnits can produce noop results. Partial WorkUnits can produce
resumable results. Conflicting WorkUnits can produce quarantined results.
Blocked WorkUnits can report the missing prerequisite without performing the
blocked action.

## Runtime Boundary

This model prepares dry-run runner planning and result validation. It does not
execute WorkUnits, call networks, call models, create local state, or mutate the
master-index.
