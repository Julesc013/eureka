# Live Metadata Candidate Snapshot Section

The live metadata candidate section records redacted Internet Archive metadata
observations as public-search-visible candidates.

Required posture:

- `source_family: internet_archive_metadata`
- `review_required: true`
- `accepted_truth: false`
- `reviewed_record_ref: null`
- `raw_response_included: false`
- `public_search_status: candidate`

The section may be rendered by public search view models, but it must never be
merged into reviewed-record sections without a later operator review and local
apply gate.
