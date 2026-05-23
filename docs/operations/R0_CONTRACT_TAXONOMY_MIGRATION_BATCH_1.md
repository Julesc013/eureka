# R0 Contract Taxonomy Migration Batch 1

R0-03B-1 executed the first contract taxonomy migration batch using the R0-03A migration plan.

## What Moved

- moved schemas: 278
- moved classes: audit_schema, fixture_schema, preview_schema
- target roots: contracts/schema/control/audits/, contracts/schema/control/fixtures/, contracts/schema/control/previews/

## What Did Not Move

- product contracts remained in contracts/
- unknown contracts remained in contracts/
- schemas with runtime or unsupported active references remained in place
- task, validator, generated, deprecated, and generic control schemas are deferred to R0-03B-2

## References And Shims

Allowed references were updated only when `--update-references` was used. Historical audit body references were left intact as evidence.
No compatibility schema files were left under contracts/; path mappings are recorded in the shim report.

## Boundaries

- no runtime files were modified
- no product behavior changed
- no schemas were deleted
- no live/network/model/provider calls were made
- F0 remains blocked
- dev-to-main promotion remains blocked

## Next

R0-03B-2 should update remaining references and clean up product contract placement after the control schema move.
