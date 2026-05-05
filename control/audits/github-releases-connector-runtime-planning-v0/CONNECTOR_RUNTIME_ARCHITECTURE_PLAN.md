# Connector Runtime Architecture Plan

Future modules only:

```text
runtime/connectors/github_releases/
  client.py              future bounded release metadata HTTP client
  repo_policy.py         owner/repo identity and allowlist guard
  policy.py              source policy, rate-limit, and token guard
  normalize.py           response-to-cache normalizer
  evidence.py            cache-to-evidence observation builder
  errors.py              bounded error model
  README.md              runtime docs
```

P89 does not create or modify those runtime files.

Future dependencies:

- source sync worker
- repository identity guard
- token/auth policy guard
- source policy guard
- source cache writer
- evidence ledger writer
- connector health reporter
- kill switch

Required future flags:

```text
EUREKA_GITHUB_RELEASES_CONNECTOR_ENABLED=0
EUREKA_GITHUB_RELEASES_LIVE_CALLS_ENABLED=0
EUREKA_GITHUB_RELEASES_AUTH_MODE=none
EUREKA_GITHUB_RELEASES_TOKEN_ENABLED=0
EUREKA_GITHUB_RELEASES_MAX_RELEASES=10
EUREKA_GITHUB_RELEASES_TIMEOUT_MS=5000
EUREKA_GITHUB_RELEASES_RATE_LIMIT_QPS=<operator-defined>
EUREKA_GITHUB_RELEASES_USER_AGENT=<operator-defined>
EUREKA_GITHUB_RELEASES_CONTACT=<operator-defined>
EUREKA_GITHUB_RELEASES_REPOSITORY_IDENTITY_REVIEW_REQUIRED=1
EUREKA_GITHUB_RELEASES_CACHE_REQUIRED=1
EUREKA_GITHUB_RELEASES_PUBLIC_SEARCH_FANOUT=0
EUREKA_GITHUB_RELEASES_REPOSITORY_CLONE=0
EUREKA_GITHUB_RELEASES_ASSET_DOWNLOAD=0
EUREKA_GITHUB_RELEASES_SOURCE_ARCHIVE_DOWNLOAD=0
EUREKA_GITHUB_RELEASES_RAW_FILE_FETCH=0
```
