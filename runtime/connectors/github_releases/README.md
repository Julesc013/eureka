# GitHub Releases Connector

`runtime/connectors/github_releases/` contains the first bounded real-source connector slice for Eureka.

This connector:

- loads small recorded GitHub Releases source fixtures for deterministic tests
- keeps acquisition and source-loading concerns connector-owned
- feeds bounded source-backed evidence summaries into the existing normalize path
- does not define canonical object truth
- does not own provenance or trust semantics
- does not imply broad live federation, downloads, installers, or auth-backed GitHub integration

Current scope is fixture-backed only. Live acquisition remains intentionally deferred so tests stay deterministic and stdlib-only.
