# Live Metadata Review Decision

Decision classes:

- `promote_reviewed_metadata_record_preview`
- `promote_reviewed_source_lead_preview`
- `mark_useful_lead`
- `needs_more_evidence`
- `duplicate`
- `near_miss`
- `reject_wrong_object`
- `reject_wrong_version`
- `reject_low_quality`
- `block_candidate`

Promotion-preview decisions remain previews. They require local apply and snapshot refresh before any reviewed projection changes.
