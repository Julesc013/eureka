# Runtime

`runtime/` holds product execution areas. Bootstrap separates engine, gateway, and connectors so their dependencies stay explicit before any real logic is added.

- `engine/`: core resolution, preservation, reconstruction, and snapshotting logic
- `gateway/`: public-facing runtime boundary, brokering, scheduling, and publishing
- `connectors/`: bounded acquisition adapters that feed governed engine interfaces

## Taxonomy Closeout

`runtime/engine` remains the current engine/kernel boundary.

The active taxonomy now uses canonical families such as `runtime/local/`,
`runtime/source/`, `runtime/index/`, `runtime/evidence/`, `runtime/review/`,
`runtime/search/`, and `runtime/worker/`. The old first-level runtime package
names remain as wrapper-only compatibility packages for import stability; they
are not canonical implementation homes.

Future target families are recorded in
`control/policies/taxonomy_closeout_policy.json` and
`docs/architecture/PATH_TAXONOMY_CLOSEOUT.md`.
