# Runtime Taxonomy Closeout v1

## Summary

`runtime/` remains behaviorally unchanged. This closeout freezes the current flat
runtime names as compatibility paths rather than moving active packages in this
turn.

## Decision

The safe closeout mode is `freeze_current_names`.

Future migrations should move one family at a time with a migration map, import
remediation, wrapper or alias notes where needed, focused tests, and architecture
boundary validation.

## Target Families

- `runtime/local/{appliance,eval,foundry,network,operator,review,service,worker}`
- `runtime/source/{registry,cache,observation}`
- `runtime/index/{candidate,public}`
- `runtime/evidence/ledger`
- `runtime/review/queue`
- `runtime/worker/workunit_queue`
- `runtime/resolution/run`
- `runtime/query/{hunt,need,quality}`

## Runtime Pages

`runtime/pages/` is classified as runtime metadata and local dry-run packet
rendering. It is not presentation ownership. Presentation belongs under
`surfaces/web/` or `site/`.

## Non-Claims

- No runtime behavior changed.
- No source connector behavior changed.
- No public search behavior changed.
- Frozen paths are compatibility paths, not permanent object identity.
