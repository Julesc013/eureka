# Contract Gap Decisions

The task did not create a new parallel E2E contract family.

True gaps that matter now are handled as profiles and documentation for the
runner task:

- QueryIntent: existing projections plus profile.
- PreviewRecord: projection-only gap; profile now, schema later if runner proves
  need.
- IndexDelta: lifecycle/profile gap over existing rebuild/apply contracts.

No proven blocking gap required a new formal v0 schema in this task.

