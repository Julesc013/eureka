# Snapshot Live Metadata Section

`snapshot_live_metadata_candidate_section.v0` describes redacted live metadata
candidates inside the snapshot projection.

Core fields:

- `section_id`
- `source_family`
- `live_metadata_pilot_ref`
- `candidate_refs`
- `candidate_count`
- `source_observation_summary_refs`
- `review_required`
- `accepted_truth`
- `reviewed_record_refs`
- `raw_response_included`
- `limitations`
- `created_at`

The section is valid only when `review_required` is true,
`accepted_truth` is false, `reviewed_record_refs` is empty, and
`raw_response_included` is false.
