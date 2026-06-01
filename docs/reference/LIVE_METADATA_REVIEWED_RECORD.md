# Live Metadata Reviewed Record

Reviewed metadata records created by this gate have limited scope:

```text
record_type: reviewed_metadata_record
source_family: internet_archive_metadata
reviewed_claim_scope: metadata_record_only
```

They retain evidence references and limitations. They must keep these false:

- `verified_download_claim`
- `malware_clean_claim`
- `rights_clearance_claim`
- `artifact_verified`

They are local reviewed metadata records, not public/master index mutation.
