# Live Metadata Reviewed Record Model

A live metadata reviewed record is a limited metadata claim created from an
eligible reviewed metadata preview through local apply validation.

It may state that redacted Internet Archive metadata supports a reviewed
metadata record. It may not state that an artifact was downloaded, inspected,
executed, extracted, malware-clean, rights-cleared, or production-ready.

Required safety fields stay false:

- `verified_download_claim`
- `malware_clean_claim`
- `rights_clearance_claim`
- `artifact_verified`

The record keeps evidence references, source locator summaries, limitations,
and the policy that authorized the local reviewed metadata scope.
