# Connectors

`runtime/connectors/` contains bounded acquisition adapters.

Boundary notes:

- connectors may depend only on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, `runtime/engine/interfaces/normalize/**`, and governed archive contracts
- connectors must not define their own canonical object model
- connectors must not own trust semantics

Current bootstrap slice:

- `synthetic_software/` is a local-only connector-shaped adapter over governed synthetic software fixtures
- `github_releases/` is the first bounded real-source connector family, using small recorded GitHub Releases fixtures for deterministic tests
- `internet_archive_recorded/` loads tiny committed Internet Archive-like metadata and item-file fixtures only; it performs no live API calls, scraping, crawling, or external lookups
- `local_bundle_fixtures/` loads tiny committed ZIP bundle fixtures only; it does not add arbitrary local filesystem ingestion or public-alpha local path access
- Source Registry v0 now owns the governed inventory of known source records under `control/inventory/sources/`; connectors remain the runtime-side implementation adapters for records that are actually implemented
- Resolution Run Model v0 records checked source ids and families by observing the bounded normalized catalog actually consulted by current implemented connectors and mapping those checks back through Source Registry v0 where possible
- connectors own source loading only in this slice
- connectors feed bounded source-backed evidence summaries into the normalize path without defining canonical object truth or trust semantics
- connectors may also feed bounded source-backed representation and access-path summaries into the normalize path without turning those paths into final download or installer semantics
- connectors may also pair bounded representations with tiny recorded payload fixtures so later acquisition and decomposition slices can retrieve deterministic local bytes and inspect supported package members without introducing live downloading or broad extraction behavior
- connectors may also feed bounded compatibility hints into the normalize path without turning them into a final compatibility oracle or installer decision
- optional live acquisition remains deferred so tests stay deterministic, stdlib-only, and easy to inspect
- extract and normalize steps remain engine-owned boundary logic
- placeholder source-registry records must not be described as implemented connectors or as checked sources in resolution runs until runtime code lands for them
