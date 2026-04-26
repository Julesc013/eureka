# Runtime Source Registry

`runtime/source_registry/` is the runtime-side loader for Source Registry v0.

Current scope:

- load governed source records from `control/inventory/sources/`
- validate required fields structurally with Python stdlib only
- expose typed runtime records for listing, lookup, and simple filtering
- load explicit source capability and source coverage-depth objects
- filter by coverage depth, capability flag, connector mode, status/posture,
  family, role, and surface

Source Coverage and Capability Model v0 is metadata only. It makes the
registry answer what each source can do today and how deeply that source is
currently indexed. It does not add acquisition behavior.

Coverage depth ladder:

0. `source_known`
1. `catalog_indexed`
2. `metadata_indexed`
3. `representation_indexed`
4. `content_or_member_indexed`
5. `action_indexed`

Source check-state terms for future runs:

- `source registered`: the source has a governed registry record
- `source eligible`: a future resolver may consider the source for a query
- `source checked`: a run actually inspected the bounded source slice
- `source returned candidate`: the source produced one or more candidate records
- `source produced evidence`: candidates carried evidence into the result
- `source skipped`: the source was intentionally not checked
- `source unavailable`: the source could not be checked within the current bounded mode

These terms are documentation vocabulary for now; this slice does not refactor
resolution runs to use a full source-check lifecycle.

Out of scope here:

- live sync
- crawling
- source health scoring
- trust scoring
- auth
- async workers
- background scheduling
- production deployment semantics

Source Registry v0 is inventory metadata only. Placeholder and future records do
not imply implemented connectors.

Real Source Coverage Pack v0 adds two active fixture-backed source records:

- `internet-archive-recorded-fixtures`: recorded metadata and item-file fixture
  shapes only, with no live Internet Archive API calls, scraping, or crawling.
- `local-bundle-fixtures`: committed local ZIP fixture corpus only, with no
  arbitrary user filesystem ingestion.

The separate `internet-archive-placeholder` and `local-files-placeholder`
records remain planning anchors and must not be presented as implemented live
connectors.
