# Session Runtime Summary

HUNT-01 adds `runtime/search/hunt` and the `SearchHuntStore`. The store persists local investigation sessions, state transitions, checked/unchecked layers, reviewed-index search summaries, and local absence summaries.

The runtime is record-only. It creates no WorkUnits, executes no source probes, calls no model providers, and does not mutate review or index stores.
