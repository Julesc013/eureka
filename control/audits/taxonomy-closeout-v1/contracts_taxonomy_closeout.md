# Contracts Taxonomy Closeout v1

## Summary

`contracts/` remains the machine-readable authority root. This closeout does not
mass-rename contract families. It records compatibility paths and target homes so
future moves can update references, validators, docs, and fixtures deliberately.

## Control Schemas

`contracts/control_schemas/` is explicitly classified as a compatibility
authority for migrated control schemas. The canonical target is
`contracts/schema/control/`, but the move is deferred until references can be
updated safely.

## Migration Mode

Migration map first. Physical moves later.

## Non-Claims

- No contract semantics changed.
- No source connector behavior changed.
- No public search behavior changed.
- Path names are not object identity.
