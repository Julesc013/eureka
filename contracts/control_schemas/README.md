# Control Schemas

`contracts/control_schemas/` is a compatibility authority path for migrated
control-plane schemas. It holds audit, fixture, preview, policy, validator, task,
and deprecated schemas that are not stable product runtime contracts.

Canonical target: `contracts/schema/control/`.

This directory is not active runtime behavior and must not be imported as
runtime implementation. Future cleanup should move one schema family at a time
with reference remediation, validator updates, and a migration map.
