# Path Taxonomy Closeout

This closeout records remaining second-level taxonomy decisions after the root
reconciliation. It is a no behavior change architecture-maintenance pass.

## Runtime

`runtime/engine` remains the engine/kernel boundary. Substantive runtime files
now live under canonical families. Old first-level runtime package names remain
only as wrapper-only compatibility packages so existing imports do not break
during the transition.

Runtime canonical families:

- `runtime/local/{appliance,eval,foundry,network,operator,review,service,worker}`
- `runtime/source/{registry,cache,observation}`
- `runtime/index/{candidate,public}`
- `runtime/evidence/ledger`
- `runtime/review/queue`
- `runtime/worker/workunit_queue`
- `runtime/resolution_run`
- `runtime/search/{hunt,need,quality}`

## Contracts

Contract moves were migration map first. `contracts/schema/control/` is the
compatibility authority path and canonical target for migrated control-plane
schemas. Parallel source, evidence, search, index, view, pack, command,
representation, and surface families now live under canonical homes recorded in
`control/audits/eureka-structure-final-closeout-v1/path_migration_map.json`.

## Examples

Examples remain public-safe fixture material. High-volume source, evidence,
pack, review, index, search, and work-unit examples now use durable families
such as `examples/packs`, `examples/sources`, `examples/search`,
`examples/review`, `examples/evidence`, `examples/index`, and
`examples/work_units`. Remaining first-level example debt is explicitly
classified for later family-specific review.

## AIDE

`.aide/` is repo operating metadata only. Export-only and generated areas are not
active source and not product truth.

## Rules

- Use migration map first for any future contract, runtime, and example family moves.
- Preserve `runtime/engine` as the current boundary.
- Do not treat generated output as source truth.
- Do not treat paths as object identity.
- Do not change product behavior, source connector behavior, or public search
  behavior as part of taxonomy cleanup.
