# Snapshot Limited Reviewed Records

Limited reviewed metadata records and limited reviewed source leads improve
review usefulness, but they keep a narrow claim scope.

They may support public-search result cards as `reviewed_metadata_record` or
`reviewed_source_lead` states. They must stay distinct from verified artifact
records.

Required non-claims:

- `artifact_verified: false`
- `verified_download_claim: false`
- `malware_clean_claim: false`
- `rights_clearance_claim: false`
- no compatibility guarantee
- no scan-completeness or OCR-quality claim
