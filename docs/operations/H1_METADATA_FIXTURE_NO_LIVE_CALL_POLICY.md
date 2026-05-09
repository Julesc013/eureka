# H1 Metadata Fixture No Live Call Policy

H1-BUNDLE-02 forbids live source calls, external calls, API calls, browser automation, model/provider calls, endpoint probes, downloads, scraping, crawling, source sync, and public-query fanout.

Fixtures must record `live_call_used: false`, `network_used: false`, and `external_api_used: false`. Outputs must not claim accepted truth, public/master index mutation, rights clearance, malware safety, verified installability, download permission, or production readiness.
