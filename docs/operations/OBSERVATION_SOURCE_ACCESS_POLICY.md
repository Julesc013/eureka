# Observation Source Access Policy

This policy defines source access modes for observation work. It does not approve any current live source access.

## Source Access Modes

- repo_local_only: committed fixtures, reports, tests, and eval outputs only.
- manual_human_only: humans may operate the source manually.
- approved_api_future: future API access after explicit source policy approval.
- approved_metadata_probe_future: future bounded metadata probe after explicit approval.
- approved_fixture_only: committed fixture or static export only.
- approved_static_dump_future: future approved static dump ingestion.
- permission_needed: source requires permission or contact before use.
- robots_blocked: automated access blocked by robots posture.
- terms_blocked: automated access blocked by terms posture.
- restricted_demand_signal_only: source may inform demand only, not evidence.
- no_autonomous_access: no agent or runtime access.

Google web search observation by agents requires an approved API path or remains manual-human-only. This policy does not authorize scraping Google result pages.

## Approval Requirements

An approved source policy must define:

- source_id
- source family
- allowed endpoint or path
- forbidden endpoint or path
- rate limit
- timeout
- retry policy
- cache TTL
- User-Agent/contact policy
- kill switch
- terms/robots posture
- privacy posture
- rights/risk posture
- operator approval
- review requirement

Without these fields, agents remain in repo-local or manual-human-only modes.
