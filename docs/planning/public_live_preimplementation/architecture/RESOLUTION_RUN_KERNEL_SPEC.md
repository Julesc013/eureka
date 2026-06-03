# Resolution Run Kernel Spec

## Role

The ResolutionRunKernel owns governed run behavior. It creates replayable runs,
emits events, schedules WorkUnits, records policy decisions, and returns lane
snapshots or run output.

## Required States

```text
created
local_lookup
needs_fallback
work_units_created
observations_received
candidates_created
review_pending
completed
blocked
failed
```

## Required Events

- run created
- local lookup attempted
- local lookup insufficient or unavailable
- fallback requested
- policy evaluated
- WorkUnit created
- SourceObservation received
- candidate created
- need created
- run blocked
- run completed

## Gate

No fallback, source adapter, or public search path can bypass the kernel.

