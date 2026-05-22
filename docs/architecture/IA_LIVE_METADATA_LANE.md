# IA Live Metadata Lane

The IA live metadata lane is an explicit, operator-approved source action for
ResolutionRunKernel runs. It is projected into the local Workbench as a lane,
but the Workbench does not own source behavior or search semantics.

Default behavior:

- The lane is visible as blocked or pending approval.
- Dry-run and mock-live paths are available for local validation.
- Real IA metadata access requires an operator command, token, policy gate, and
  bounded request limits.
- Public and native read-only projections cannot run live source actions.

Boundaries:

- No live IA call by default.
- No public fanout.
- No downloads, uploads, extraction, execution, or model/provider calls.
- No raw live response body is committed.
- No accepted evidence, reviewed record, master index mutation, or operator
  instance mutation is created by this lane.

The lane creates projection-safe source observations and provisional result
lane candidates only. Review and promotion are deferred to the Workbench review
flow.
