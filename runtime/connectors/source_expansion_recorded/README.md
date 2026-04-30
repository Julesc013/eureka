# Source Expansion Recorded Fixtures

This connector replays the tiny committed fixture pack for Search Usefulness
Source Expansion v2. It is recorded-fixture-only: it performs no network calls,
scraping, crawling, live probes, artifact downloads, installer handling, or
external baseline observations.

Each fixture record carries its own `source_family` so the local index and
public search result cards can distinguish Wayback/Memento, Software Heritage,
SourceForge, package-registry, manual/document, and review/description evidence
without creating live connectors for those systems.
