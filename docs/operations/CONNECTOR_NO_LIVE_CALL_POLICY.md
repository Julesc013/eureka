# Connector No-Live-Call Policy

H0-BUNDLE-02 does not enable live source calls, live probes, source sync,
downloads, scraping, crawling, arbitrary URL fetches, public-query fanout,
model/provider calls, public-index mutation, master-index mutation, or truth
acceptance.

Connector contracts, capabilities, fixture replay, live-probe envelopes, and
policy evaluations are governance and offline validation tools. Future H tasks
must explicitly approve any live behavior and record the approval, bounded
request, output paths, review gates, and post-run audit evidence.
