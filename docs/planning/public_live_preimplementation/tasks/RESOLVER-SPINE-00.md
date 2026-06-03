# RESOLVER-SPINE-00

Goal: align existing resolver runtime paths behind one governed spine.

Inputs to read first: `architecture/RESOLVER_SPINE_SPEC.md`,
`runtime/resolution_run/**`, `runtime/engine/resolution_runs/**`,
`runtime/source/observation/**`, `runtime/review/**`.

Allowed paths: runtime resolver paths selected by preflight, matching tests,
docs/operations runbooks, control inventories.

Protected paths: unrelated runtime, public index mutation, source downloads,
deployment.

Deliverables: authoritative path decision, minimal spine behavior or adapter,
focused tests, validation report.

Non-goals: full rewrite, public launch, broad source expansion.

Validation: resolution-run kernel tests, architecture boundary check, focused
changed/failed-first lane.

Exit criteria: fallback can be implemented without a parallel search path.

Impact statement: runtime/code impact required.

