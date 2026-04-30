# Live Probe Gateway Contract

Live Probe Gateway Contract v0 defines the disabled-by-default policy boundary
for any future external metadata probe. It is not a probe implementation and it
does not call Internet Archive, Wayback, GitHub, Software Heritage, package
registries, Wikidata, Google, or any external source.

The gateway sits behind the future live backend handoff. Static publication
surfaces may describe that the gateway contract exists, but they must not imply
that live probes are available.

Public Search API Contract v0 does not use live probes. Its first allowed mode
is `local_index_only`, and its request schema rejects live-probe mode, URL
fetch, downloads, installs, uploads, local path search, and source credentials.

## Rules

- Live probes are disabled by default.
- Public-alpha live probes are disabled by default.
- Every source requires explicit operator enablement and source-policy review.
- Metadata-first behavior is required.
- Cache-first and evidence-first behavior are required.
- Downloads are not allowed by this contract.
- Arbitrary URL fetching is not allowed.
- Scraping and bulk crawling are not allowed.
- User credentials and private account data must not be forwarded to sources.
- Source-specific timeouts, result caps, retry limits, and circuit breakers are
  required before any implementation.
- External terms, robots expectations, and abuse posture require human review
  before a source is enabled.

## Candidate Sources

The v0 candidate source list is recorded in
`control/inventory/publication/live_probe_gateway.json`. Every candidate is
`future_disabled` and `live_supported_now=false`.

Current candidates are metadata-only or availability-oriented:

- `internet_archive_metadata`
- `internet_archive_item_metadata`
- `wayback_availability`
- `wayback_cdx_metadata`
- `github_releases_metadata`
- `software_heritage_metadata`
- `pypi_package_metadata`
- `npm_package_metadata`
- `wikidata_metadata`

Google is not a live probe candidate. It remains a manual external-baseline
system only.

## Response Envelope

A future disabled/live-probe response should be explicit about source, status,
limits, and evidence posture:

```json
{
  "ok": true,
  "source_id": "internet_archive_metadata",
  "probe_status": "disabled",
  "query": "example query",
  "results": [],
  "evidence_records": [],
  "notices": [
    "Live probes are disabled in this static/public-alpha build."
  ],
  "limits": {
    "max_total_results": 20,
    "max_results_per_source": 10,
    "source_timeout_ms": 5000
  }
}
```

Errors must align with the live backend error envelope. Required relevant codes
include `capability_disabled`, `live_probes_disabled`, `source_disabled`,
`source_timeout`, `rate_limited`, and `bad_request`.

## Not Implemented

This milestone adds no adapters, no endpoint handlers, no public search
runtime, no URL fetching, no live Internet Archive behavior, no crawling, no
scraping, no downloads, no auth, and no production API stability promise.
