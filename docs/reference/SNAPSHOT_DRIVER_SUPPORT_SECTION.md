# Snapshot Driver/Support Section Reference

Required fields:

- `schema_version`
- `section_id`
- `domain_id: driver_support_media`
- `candidate_count`
- `candidate_refs`
- `download_performed: false`
- `file_fetch_performed: false`
- `install_execution_enabled: false`
- `malware_clean_claim_created: false`
- `compatibility_guarantee_created: false`
- `rights_clearance_claim_created: false`
- `accepted_truth: false`
- `limitations`

Public search cards from this section must use candidate status. They are not
verified driver packages and do not expose download, malware-clean,
compatibility, install/execution, or rights-clearance claims.
