# Versioning Policy

Public data files use `schema_version` fields, currently `0.1.0`.

Versioning rules:

- Consumers must check `schema_version` before interpreting a file.
- `stable_draft` fields may be consumed by pre-alpha static clients, snapshots,
  future relay prototypes, and future native clients only with version checks.
- `experimental` fields may be displayed but should not drive durable branching
  unless the client pins to a known schema version.
- `volatile` fields may change value or wording between generated artifacts and
  should be diagnostic only.
- `internal` fields are repo/generator implementation details and are not public
  client API.
- `future` fields are reserved for later contracts and do not imply current
  implementation.
- `deprecated` fields must remain documented until a later migration removes
  them with a breaking-change note.

No current public JSON file is production-stable. A later production API or
production public-data promise would need a separate approval milestone,
compatibility tests, changelog process, and release discipline.
