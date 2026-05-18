# Live Probe Policy

IA-02 permits only an explicitly approved metadata-only local probe.

- approval flag required: `--approve-live`
- allowed domain: `archive.org`
- endpoint classes: `metadata_search_small`, `item_metadata_read`
- metadata search rows: at most 1
- total HTTP requests: at most 2
- timeout: at most 10 seconds
- User-Agent and contact required
- kill switch checked before requests
- raw response body commits forbidden

Downloads, uploads, write APIs, public fanout, source-cache writes, evidence
writes, candidate/reviewed/master index mutation, extraction, model/provider
calls, deployment, production readiness claims, and public launch claims remain
forbidden.
