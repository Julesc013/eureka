# Connectors

`runtime/connectors/` contains bounded acquisition adapters.

Boundary notes:

- connectors may depend only on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, `runtime/engine/interfaces/normalize/**`, and governed archive contracts
- connectors must not define their own canonical object model
- connectors must not own trust semantics

Current bootstrap slice:

- `synthetic_software/` is a local-only connector-shaped adapter over governed synthetic software fixtures
- `github_releases/` is the first bounded real-source connector family, using small recorded GitHub Releases fixtures for deterministic tests
- connectors own source loading only in this slice
- connectors feed bounded source-backed evidence summaries into the normalize path without defining canonical object truth or trust semantics
- optional live acquisition remains deferred so tests stay deterministic, stdlib-only, and easy to inspect
- extract and normalize steps remain engine-owned boundary logic
