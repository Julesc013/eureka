# Live Metadata Promotion Preview

A live metadata promotion preview is not promotion.

Allowed preview kinds:

- `reviewed_metadata_record`
- `reviewed_source_lead`

Disallowed claims:

- `verified_download`
- `safe_installer`
- `extracted_file`
- `malware_clean`
- `rights_cleared`
- `production_quality_artifact`

The preview records a possible local apply input. It must pass a separate operator gate before any reviewed record mutation, then a separate snapshot refresh before public-facing projections can change.
