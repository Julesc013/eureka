# Source Inventory

This directory holds the governed seed records for Source Registry v0.

Current scope:

- inventory and labeling only
- explicit source roles, surfaces, connector ownership, and posture metadata
- explicit source capabilities and coverage-depth metadata
- active fixture-backed and active recorded-fixture-backed seed sources plus
  honest placeholder or future entries

Source Registry v0 does **not** imply:

- live sync
- crawling
- source health scoring
- trust scoring
- authentication
- async workers
- production deployment semantics

Source Coverage and Capability Model v0 adds two required fields to every seed
record:

- `capabilities`: bounded booleans describing what the current source slice can
  do, such as search, item metadata, file listing, member listing, hashes,
  action paths, local privacy, fixture backing, recorded fixture backing, and
  live-deferred posture.
- `coverage`: the current indexed depth and next coverage step.

Coverage depth values are:

- `source_known`
- `catalog_indexed`
- `metadata_indexed`
- `representation_indexed`
- `content_or_member_indexed`
- `action_indexed`

Depth describes current bounded implementation only. Placeholder sources must
remain `source_known` unless a later accepted recorded-fixture or connector
milestone changes the source posture.

Seed records currently cover:

- `synthetic-fixtures`
- `github-releases-recorded-fixtures`
- `internet-archive-recorded-fixtures`
- `local-bundle-fixtures`
- `internet-archive-placeholder`
- `wayback-memento-placeholder`
- `software-heritage-placeholder`
- `local-files-placeholder`

Real Source Coverage Pack v0 adds `internet-archive-recorded-fixtures` and
`local-bundle-fixtures` as active fixture-backed source records. They are tiny
committed test fixtures for old-platform software and bundle/member discovery.
They do not call the Internet Archive API, scrape external sites, crawl,
federate sources, or ingest arbitrary user filesystem paths.

Old-Platform Source Coverage Expansion v0 expands those same active fixture
records with more committed source-shaped evidence for old Windows/Mac browser
notes, utility and registry-repair cases, and driver/support-media member
paths. It does not promote any placeholder source and it still adds no live
Internet Archive API calls, scraping, crawling, broad source federation, or
arbitrary local filesystem ingestion.

Placeholder and future records are planning anchors only. They must not be
described as implemented connectors until runtime code lands for them.
