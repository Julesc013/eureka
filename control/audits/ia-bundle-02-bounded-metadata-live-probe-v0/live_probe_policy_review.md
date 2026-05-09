# Live Probe Policy Review

Decision: `BLOCKED`.

The committed IA-BUNDLE-01 and IA-BUNDLE-02 policy files do not approve a live
metadata call. The live probe runtime therefore fails closed before any network
operation.

Required approval decisions before a future live run:

- set `internet_archive_source_policy.live_access_approved` to `true`
- set `internet_archive_source_policy.metadata_probe_approved` to `true`
- keep file download, item file fetch, scraping, and public fanout approvals `false`
- approve exactly one metadata endpoint template: `https://archive.org/metadata/{identifier}`
- approve a non-placeholder User-Agent/contact posture or explicit omission
- set timeout, request budget, retry, and cache/no-cache decisions
- set the kill switch to allow exactly this one probe
- add the exact operator-approved identifier to the allowed identifier list

No Internet Archive call was made in IA-BUNDLE-02.
