# Source Cache Record Classification

The classifier uses conservative dimensions:

- `source_family`: `internet_archive`, `wayback_cdx_memento`, `github_releases`, `pypi`, `npm`, `software_heritage`, `local_fixture`, `unknown`
- `record_kind`: `metadata_summary`, `availability_summary`, `capture_metadata_summary`, `release_metadata_summary`, `package_metadata_summary`, `software_identity_summary`, `unknown`
- `privacy_status`: `public_safe`, `redacted`, `local_private`, `rejected_sensitive`, `unknown`
- `public_safety_status`: `public_safe`, `review_required`, `rejected`, `unknown`
- `evidence_readiness`: `evidence_candidate_ready`, `evidence_review_required`, `insufficient`, `not_applicable`, `unknown`
- `policy_status`: `approved_example`, `approval_required`, `operator_required`, `blocked_by_policy`, `unknown`

Unknown or unsupported required values make a candidate invalid in strict mode.
