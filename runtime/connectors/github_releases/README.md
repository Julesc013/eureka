# GitHub Releases Connector

`runtime/connectors/github_releases/` contains the first bounded real-source connector slice for Eureka.

This connector:

- loads small recorded GitHub Releases source fixtures for deterministic tests
- keeps acquisition and source-loading concerns connector-owned
- feeds bounded source-backed evidence summaries into the existing normalize path
- feeds bounded release-page and release-asset representation summaries into the existing normalize path without implying actual download behavior
- pairs bounded release-asset representations with tiny recorded local payload fixtures so acquisition tests can retrieve deterministic bytes without live network access
- keeps those recorded payload fixtures small and inspectable so supported formats can later surface bounded package-member listings without implying live downloads, installers, or broad extraction behavior
- may feed small recorded compatibility hints into the existing normalize path without implying a final compatibility oracle or installer decision
- does not define canonical object truth
- does not own provenance or trust semantics
- does not imply broad live federation, downloads, installers, or auth-backed GitHub integration

Current scope is fixture-backed only. Live acquisition remains intentionally deferred so tests stay deterministic and stdlib-only.
