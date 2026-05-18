# Promotion Preview Schema

Promotion previews include a proposed reviewed-record id, title, summary,
source locator, source-cache ids, evidence ids, provenance, uncertainty,
limitations, rights flags, and risk flags.

Promotion previews are preview-only and keep:

- `reviewed_index_write_performed: false`
- `master_index_write_performed: false`
- `accepted_truth: false`
- `raw_response_committed: false`
- `download_performed: false`

