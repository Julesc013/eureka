# R0 Contract Taxonomy Refactor Plan

R0-03A is a planning task. It classifies the current contents of `contracts/**`
and produces the exact migration plan for R0-03B. It does not move files,
delete files, refactor runtime, or change product behavior.

## What R0-03A Found

The current contract tree mixes product contracts with control schemas. Stable
product boundaries sit beside audit reports, fixture replay schemas, preview
candidates, task queue records, quality-delta schemas, and phase-named connector
artifacts.

The machine-readable inventory is:

- `control/inventory/contract_taxonomy_inventory.json`
- `control/inventory/contract_migration_plan.json`
- `control/inventory/contract_reference_graph.json`
- `control/inventory/contract_risk_register.json`
- `control/inventory/r0_03b_execution_plan.json`

## Why Moving Is Deferred

R0-03A must keep `contracts/**` unchanged so the plan can be reviewed before
R0-03B touches product-boundary paths. Moving schemas also requires reference
updates across scripts, tests, examples, runtime static references, and audit
evidence. Doing that without a deterministic plan would make the recovery work
harder to review.

## Migration Batches

R0-03B is expected to split into batches because the migration touches more
than a small one-shot refactor:

1. `R0-03B-1 — Create target schema roots and move audit/fixture/preview schemas`
2. `R0-03B-2 — Update references and validators`
3. `R0-03B-3 — Product contract cleanup and compatibility audit`

The batch contents are generated in
`control/inventory/r0_03b_execution_plan.json`.

## Compatibility Risks

The largest risk is stale path references. R0-03B must update validators, tests,
examples, and static runtime references that point at moved schemas.

Compatibility shims or aliases are required where old paths still need to be
accepted temporarily during the migration. Deletion is not part of R0-03B unless
a later task proves an artifact is unreferenced after quarantine.

## Reference Update Strategy

R0-03A builds a path-literal reference graph from:

- `contracts/**`
- `control/audits/**`
- `examples/**`
- `scripts/**`
- `tests/**`
- `runtime/**` by static text scanning only

R0-03B should update references by batch, then rerun the taxonomy audit and the
runtime architecture leakage gate.

## Validation Strategy

Required validation after R0-03B moves:

- `python scripts/audit_contract_taxonomy.py --check --json`
- `python scripts/validate_contract_taxonomy_plan.py`
- `python scripts/validate_runtime_architecture_leakage.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`

## F0 Status

F0 remains blocked because contract taxonomy is still mixed. A feature task
cannot safely treat artifact existence as product completion until product
contracts and control schemas are separated and validated.

Dev-to-main promotion also remains blocked.
