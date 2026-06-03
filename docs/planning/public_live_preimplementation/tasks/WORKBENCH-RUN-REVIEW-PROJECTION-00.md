# WORKBENCH-RUN-REVIEW-PROJECTION-00

Goal: make fallback/run/review evidence visible in Workbench without separate
truth semantics.

Inputs to read first: `workbench/*.md`, `surfaces/web/workbench/**`,
`runtime/gateway/public_api/resolution_runs_*`, review docs.

Allowed paths: Workbench surfaces, gateway view models, focused tests, docs.

Protected paths: public mutation, source adapters unless only projection data
is needed.

Deliverables: Workbench views/actions for runs, WorkUnits, observations,
candidates, needs, review events, and index builds.

Non-goals: public Workbench, bypassing review ledger.

Validation: Workbench rendering/API tests and review boundary tests.

Exit criteria: public reviewed records trace back through Workbench-visible
state.

Impact statement: surface/UI and gateway projection impact.

