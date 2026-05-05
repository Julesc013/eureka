# Public Index And Result Envelope Gate Review

Status: present for local/static public search.

Public index format:

- `docs/reference/PUBLIC_SEARCH_INDEX_FORMAT.md`
- `data/public_index/build_manifest.json`
- `data/public_index/source_coverage.json`
- `data/public_index/index_stats.json`
- `data/public_index/search_documents.ndjson`
- `data/public_index/checksums.sha256`

Current index facts from `index_stats.json`:

- 584 documents.
- `live_sources_used: false`
- `external_calls_performed: false`
- `private_paths_detected: false`
- `executable_payloads_included: false`

Result envelope support:

- Result IDs and public document IDs are available.
- Source refs and source family/status fields are available.
- Evidence summaries and compatibility summaries are available.
- Lane/status fields are available through result-lane and public card fields.
- Gap, warning, limitation, blocked action, and allowed action fields are
  available.

Gaps:

- Explanation refs are future-only.
- Ranking runtime output is not available as authoritative input.
- Source-cache/evidence-ledger authoritative refs are not available for P106.

