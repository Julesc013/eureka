# Runtime

`runtime/` holds product execution areas. Bootstrap separates engine, gateway, and connectors so their dependencies stay explicit before any real logic is added.

- `engine/`: core resolution, preservation, reconstruction, and snapshotting logic
- `gateway/`: public-facing runtime boundary, brokering, scheduling, and publishing
- `connectors/`: bounded acquisition adapters that feed governed engine interfaces

## Taxonomy Closeout

`runtime/engine` remains the current engine/kernel boundary.

The remaining flat runtime package names are taxonomy-closeout compatibility
paths. Current names are frozen until a family-by-family migration can update
imports, validators, docs, examples, and tests without changing product
behavior.

Future target families are recorded in
`control/policies/taxonomy_closeout_policy.json` and
`docs/architecture/PATH_TAXONOMY_CLOSEOUT.md`.
