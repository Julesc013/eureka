# Live Call Block Report

IA-BUNDLE-01 performs no external calls. The runtime module and CLI use local
JSON fixture loading only.

Blocked behaviors:

- Internet Archive live source calls
- external URLs and API calls
- live probes
- source sync
- downloads and item file fetches
- scraping and crawling
- browser automation
- model/provider calls
- public query fanout
- public/master index mutation

The validator scans the IA runtime and scripts for network-capable imports and
checks fixture, normalized, source-cache preview, evidence preview, audit, and
policy booleans for forbidden true claims.
