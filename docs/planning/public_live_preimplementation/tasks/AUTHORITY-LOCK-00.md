# AUTHORITY-LOCK-00

Goal: refresh current repo authority before implementation.

Inputs to read first: `README.md`, `.aide/queue/index.yaml`,
`control/inventory/*result.json`, `docs/operations/PUBLIC_ALPHA_LAUNCH_DEFERRED.md`.

Allowed paths: `docs/planning/**`, `control/audits/**`, `control/inventory/**`.

Protected paths: `docs/canon/**`, `contracts/**`, `runtime/**`, `surfaces/**`,
`.aide/queue/current.toml`.

Deliverables: current repo reality, queue map, protected paths report, claims
requiring verification.

Non-goals: runtime code, contract promotion, queue mutation, launch claim.

Validation: `git status --short`, `git diff --check`, focused docs checks.

Exit criteria: current authority state is explicit and no archive/vision claim
is promoted.

Impact statement: docs-only authority impact; no canon/contract/runtime/surface
impact.

