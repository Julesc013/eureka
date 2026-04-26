# Synthetic Records

`runtime/engine/synthetic_records/` owns deterministic records derived from
existing bounded fixture evidence.

Member-Level Synthetic Records v0 creates `synthetic_member` records for useful
files inside committed local bundle fixtures. A synthetic member record is not a
new external source and not a new canonical truth claim. It preserves:

- a deterministic `member:sha256:<digest>` target ref
- parent target ref and parent representation id
- source id/family/label
- member path, inferred member kind, media type, size, and hash when available
- member-listing/readme/compatibility evidence from the bounded fixture
- action hints for existing inspect/read/preview flows

This module deliberately does not add live source probing, crawling, broad
archive extraction, arbitrary local filesystem ingestion, ranking, or Rust
runtime behavior.
