# Connector Runtime Architecture Plan

Future modules only:

```text
runtime/connectors/pypi_metadata/
  client.py              future bounded metadata HTTP client
  package_policy.py      package-name identity and allowlist guard
  dependency_policy.py   dependency metadata caution guard
  policy.py              source policy, rate-limit, and token guard
  normalize.py           response-to-cache normalizer
  evidence.py            cache-to-evidence observation builder
  errors.py              bounded error model
  README.md              runtime docs
```

P90 does not create or modify those runtime files.

Future dependencies:

- source sync worker
- package identity guard
- dependency metadata caution guard
- token/auth policy guard
- source policy guard
- source cache writer
- evidence ledger writer
- connector health reporter
- kill switch

Required future flags:

```text
EUREKA_PYPI_METADATA_CONNECTOR_ENABLED=0
EUREKA_PYPI_METADATA_LIVE_CALLS_ENABLED=0
EUREKA_PYPI_METADATA_AUTH_MODE=none
EUREKA_PYPI_METADATA_TOKEN_ENABLED=0
EUREKA_PYPI_METADATA_MAX_RELEASES=20
EUREKA_PYPI_METADATA_MAX_FILES=50
EUREKA_PYPI_METADATA_TIMEOUT_MS=5000
EUREKA_PYPI_METADATA_RATE_LIMIT_QPS=<operator-defined>
EUREKA_PYPI_METADATA_USER_AGENT=<operator-defined>
EUREKA_PYPI_METADATA_CONTACT=<operator-defined>
EUREKA_PYPI_METADATA_PACKAGE_IDENTITY_REVIEW_REQUIRED=1
EUREKA_PYPI_METADATA_DEPENDENCY_RESOLUTION=0
EUREKA_PYPI_METADATA_PACKAGE_DOWNLOAD=0
EUREKA_PYPI_METADATA_WHEEL_DOWNLOAD=0
EUREKA_PYPI_METADATA_SDIST_DOWNLOAD=0
EUREKA_PYPI_METADATA_PACKAGE_INSTALL=0
EUREKA_PYPI_METADATA_ARCHIVE_INSPECTION=0
EUREKA_PYPI_METADATA_CACHE_REQUIRED=1
EUREKA_PYPI_METADATA_PUBLIC_SEARCH_FANOUT=0
```
