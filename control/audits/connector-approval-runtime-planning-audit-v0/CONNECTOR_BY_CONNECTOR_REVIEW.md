# Connector By Connector Review

All connectors share the same aggregate posture: approval pack present, runtime
planning pack present, approval pending, live runtime disabled, public-search
fanout disabled, downloads/install/execution disabled, credentials/tokens
disabled, and mutation disabled.

Connector-specific risks are recorded in the individual review files:

- `INTERNET_ARCHIVE_METADATA_REVIEW.md`
- `WAYBACK_CDX_MEMENTO_REVIEW.md`
- `GITHUB_RELEASES_REVIEW.md`
- `PYPI_METADATA_REVIEW.md`
- `NPM_METADATA_REVIEW.md`
- `SOFTWARE_HERITAGE_REVIEW.md`

The next safe action for all connectors is human/operator review of source/API
policies, User-Agent/contact policy, rate-limit/timeout/circuit-breaker policy,
identity/privacy boundaries, and source-cache/evidence-ledger destination policy.
