# Acquisition Evidence Checklist

This handoff is not a download or install task. Acquisition evidence is limited
to source-backed descriptions of whether a safe, policy-approved acquisition or
reproducibility path may exist.

## Allowed To Record

- source states that an artifact is available
- source gives a catalog, release, package, page, or member locator
- source documents a checksum, signature, or release manifest
- source documents access requirements, authentication, region, or entitlement
- source states that an item is unavailable, missing, restricted, or obsolete

## Forbidden In This Handoff

- executable binary downloads
- installer execution
- archive extraction
- emulation
- malware scanning claims
- rights clearance claims
- public availability claims
- repo-local raw source dumps, screenshots, binaries, private caches, or logs

## Review Actions

Use one of these review action recommendations:

- `promote_to_review_candidate`
- `request_more_evidence`
- `mark_near_miss`
- `mark_need`
- `mark_blocked_for_user_details`
- `reject`
- `defer`

Do not recommend `verified_artifact` unless a future verified-artifact policy
and level4 or level5 evidence explicitly support that stronger claim.
