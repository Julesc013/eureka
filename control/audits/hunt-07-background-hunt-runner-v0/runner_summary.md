# Runner Summary

The background hunt runner plans and runs bounded batches of safe deterministic local WorkUnits linked to a Search Hunt through SearchNeeds.

Modes:

- `plan`: classify linked WorkUnits as runnable or blocked without running workers.
- `run-next`: run one safe queued WorkUnit.
- `run-batch`: run up to ten safe queued WorkUnits.
- `runs` and `summary`: inspect recorded run history.

Blocked policy WorkUnits remain blocked and are reported as policy signals.

