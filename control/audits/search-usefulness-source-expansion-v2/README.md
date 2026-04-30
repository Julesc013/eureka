# Search Usefulness Source Expansion v2

Search Usefulness Source Expansion v2 is implemented as a fixture-only source coverage slice.

It adds tiny recorded/synthetic metadata fixtures for selected source-gap query families and routes them through normalization, source inventory, local index/search, and public search result cards. It does not add live probes, crawling, scraping, arbitrary URL fetches, external observations, real binaries, downloads, installs, uploads, local path search, telemetry, accounts, hosted deployment, malware-safety claims, or rights-clearance claims.

Baseline audit counts:

- covered: 5
- partial: 22
- source_gap: 26
- capability_gap: 9
- unknown: 2

Final audit counts:

- covered: 5
- partial: 40
- source_gap: 10
- capability_gap: 7
- unknown: 2

External baselines remain pending manual observation for all query rows.

