# Connector Runtime Architecture Plan

Future modules only:

```text
runtime/connectors/software_heritage/
  client.py              future bounded metadata HTTP client
  identity_policy.py     SWHID/origin/repository identity guard
  content_policy.py      source-code-content prohibition guard
  policy.py              source policy/rate-limit/token guard
  normalize.py           response-to-cache normalizer
  evidence.py            cache-to-evidence observation builder
  errors.py              bounded error model
  README.md              runtime docs
```

P92 does not create those runtime files.

Future dependencies:

- source sync worker
- SWHID/origin/repository identity guard
- source-code-content risk guard
- token/auth policy guard
- source policy guard
- source cache writer
- evidence ledger writer
- connector health reporter
- kill switch

Required future environment flags:

- EUREKA_SWH_CONNECTOR_ENABLED=0
- EUREKA_SWH_LIVE_CALLS_ENABLED=0
- EUREKA_SWH_AUTH_MODE=none
- EUREKA_SWH_TOKEN_ENABLED=0
- EUREKA_SWH_MAX_RESULTS=10
- EUREKA_SWH_TIMEOUT_MS=5000
- EUREKA_SWH_RATE_LIMIT_QPS=<operator-defined>
- EUREKA_SWH_USER_AGENT=<operator-defined>
- EUREKA_SWH_CONTACT=<operator-defined>
- EUREKA_SWH_SWHID_REVIEW_REQUIRED=1
- EUREKA_SWH_ORIGIN_REVIEW_REQUIRED=1
- EUREKA_SWH_REPOSITORY_IDENTITY_REVIEW_REQUIRED=1
- EUREKA_SWH_SOURCE_CODE_CONTENT_FETCH=0
- EUREKA_SWH_CONTENT_BLOB_FETCH=0
- EUREKA_SWH_DIRECTORY_CONTENT_FETCH=0
- EUREKA_SWH_REPOSITORY_CLONE=0
- EUREKA_SWH_SOURCE_ARCHIVE_DOWNLOAD=0
- EUREKA_SWH_ORIGIN_CRAWL=0
- EUREKA_SWH_CACHE_REQUIRED=1
- EUREKA_SWH_PUBLIC_SEARCH_FANOUT=0
