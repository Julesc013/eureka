# R0 Contract Reference Update And Product Cleanup

R0-03B-2 updated active schema references that were inside the allowed control, docs, tests, examples, and validator boundary.
It moved the remaining safe control and task schemas out of `contracts/` and into `contracts/control_schemas/`.

Historical audit evidence was left intact when it records a past contract path.
The current active schema taxonomy now lives in generated inventory files, not in older audit narrative.

## Reference Updates

- Active references updated: 2315
- Reference updates blocked: 4
- Schemas moved in this task: 49
- Runtime files modified: 0
- Product behavior changed: false

Blocked updates are tied to active consumers outside this task's write boundary.

## Contract Tree

- Contracts scanned: 279
- Product contracts remaining: 260
- Non-product contracts still under `contracts/`: 16
- Unknown contract artifacts: 3
- Task/bundle-shaped product names needing later review: 2
- Compatibility or unresolved mapping count: 19

Runtime was not touched. Remaining runtime-referenced schemas are recorded as explicit contract taxonomy debt.

- contracts clean enough for R0-04: false
- F0 remains blocked: true
- dev-to-main remains blocked: true
- next task: R0-03C — Resolve remaining contract taxonomy blockers
