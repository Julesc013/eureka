# Path Taxonomy Closeout

This closeout records remaining second-level taxonomy decisions after the root
reconciliation. It is a no behavior change architecture-maintenance pass.

## Runtime

`runtime/engine` remains the engine/kernel boundary. Current flat runtime names
are frozen as compatibility paths until a future family-by-family migration can
update imports, validators, docs, examples, and tests.

Future runtime targets:

- `runtime/local/{appliance,eval,foundry,network,operator,review,service,worker}`
- `runtime/source/{registry,cache,observation}`
- `runtime/index/{candidate,public}`
- `runtime/evidence/ledger`
- `runtime/review/queue`
- `runtime/worker/workunit_queue`
- `runtime/resolution/run`
- `runtime/query/{hunt,need,quality}`

## Contracts

Contract moves are migration map first. `contracts/control_schemas/` is a
compatibility authority path with canonical target `contracts/schema/control/`.
Parallel source, evidence, search, index, view, and surface families have target
homes in `control/audits/taxonomy-closeout-v1/contracts_taxonomy_migration_map.json`.

## Examples

Examples remain public-safe fixture material. Future moves should use durable
families such as `examples/packs`, `examples/sources`, `examples/search`,
`examples/review`, `examples/evidence`, `examples/index`, and
`examples/work_units`.

## AIDE

`.aide/` is repo operating metadata only. Export-only and generated areas are not
active source and not product truth.

## Rules

- Use migration map first for contract, runtime, and example family moves.
- Preserve `runtime/engine` as the current boundary.
- Do not treat generated output as source truth.
- Do not treat paths as object identity.
- Do not change product behavior, source connector behavior, or public search
  behavior as part of taxonomy cleanup.
