# Examples

`examples/` holds public-safe fixtures, packs, source observations, review
examples, connector examples, and audit proofs.

## Taxonomy Closeout

The highest-volume task-phase example groups have been moved into durable
families. Remaining first-level examples are classified taxonomy debt, not a
junk drawer. Durable families for current and future examples are:

- `examples/packs`
- `examples/sources`
- `examples/connectors`
- `examples/search`
- `examples/review`
- `examples/evidence`
- `examples/index`
- `examples/snapshots`
- `examples/import_reports`
- `examples/api`
- `examples/site`
- `examples/native`
- `examples/relay`
- `examples/work_units`

Further moves should use a migration map first and update checksums, references,
validators, docs, and tests in the same change. Do not collapse connector fixture
detail or change fixture meaning during taxonomy cleanup.
