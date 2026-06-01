# LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00

This task is the local-apply gate for eligible live metadata review previews.
It consumes only committed, redacted review-preview examples from the bounded
Internet Archive metadata pilot.

Eligible inputs are limited to:

- `reviewed_metadata_record_preview`
- `reviewed_source_lead_preview`

The default apply target is a temporary explicit store. Operator instance apply
is not enabled by default and requires a separate approval path.

Local apply converts eligible previews into limited local records:

- reviewed metadata records
- reviewed source leads

Those records do not claim verified downloads, safe installers, malware-clean
status, rights clearance, extraction results, or production artifact quality.

This task does not mutate reviewed, master, or public indexes. It creates
handoffs for `SNAPSHOT-REFRESH-03` and a later public alpha reassessment.
