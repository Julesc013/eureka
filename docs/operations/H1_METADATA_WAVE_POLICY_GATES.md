# H1 Metadata Wave Policy Gates

Every H1 source requires the same gate set before future live access:

- source policy approval
- endpoint allowlist
- User-Agent/contact posture
- rate limit
- timeout
- retry budget
- cache TTL
- kill switch
- fixture replay
- dry-run policy evaluation
- output path policy
- privacy/risk review
- rights posture
- review queue gate
- post-run audit
- connector scorecard

The current approval state for each source is `not_approved_for_live_access`.

## Current Allowed Operations

- `inspect_fixture`
- `normalize_fixture`
- `record_source_policy`
- `record_source_metadata_preview`
- `create_coverage_preview`
- `create_scorecard_preview`

## Current Forbidden Operations

Live probes, source sync, source-cache writes, evidence writes, package downloads, release asset downloads, source archive downloads, broad crawling, HTML scraping, public-index mutation, master-index mutation, and truth acceptance remain forbidden.
