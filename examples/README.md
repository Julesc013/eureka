# Examples

`examples/` holds public-safe fixtures, packs, source observations, review
examples, connector examples, and audit proofs.

## Taxonomy Closeout

The current first-level examples layout is classified taxonomy debt, not a junk
drawer. Durable families for future moves are:

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

Future moves should use a migration map first and update checksums, references,
validators, docs, and tests in the same change. Do not collapse connector fixture
detail or change fixture meaning during taxonomy cleanup.
