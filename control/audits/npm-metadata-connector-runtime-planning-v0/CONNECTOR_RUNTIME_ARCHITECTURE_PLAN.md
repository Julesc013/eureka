# Connector Runtime Architecture Plan

Future modules only, not created by P91:

- `runtime/connectors/npm_metadata/client.py`: future bounded metadata HTTP client.
- `runtime/connectors/npm_metadata/package_policy.py`: future package-name and scoped-package identity guard.
- `runtime/connectors/npm_metadata/dependency_policy.py`: future dependency metadata caution guard.
- `runtime/connectors/npm_metadata/script_policy.py`: future lifecycle-script metadata/risk guard.
- `runtime/connectors/npm_metadata/policy.py`: future source policy, rate-limit, and token guard.
- `runtime/connectors/npm_metadata/normalize.py`: future response-to-cache normalizer.
- `runtime/connectors/npm_metadata/evidence.py`: future cache-to-evidence observation builder.
- `runtime/connectors/npm_metadata/errors.py`: future bounded error model.
- `runtime/connectors/npm_metadata/README.md`: future runtime docs.

Future dependencies: source sync worker, package identity guard, scoped package guard, dependency metadata caution guard, lifecycle-script risk guard, token/auth policy guard, source policy guard, source cache writer, evidence ledger writer, connector health reporter, and kill switch.

Required future flags default disabled: `EUREKA_NPM_METADATA_CONNECTOR_ENABLED=0`, `EUREKA_NPM_METADATA_LIVE_CALLS_ENABLED=0`, `EUREKA_NPM_METADATA_AUTH_MODE=none`, `EUREKA_NPM_METADATA_TOKEN_ENABLED=0`, `EUREKA_NPM_METADATA_MAX_VERSIONS=20`, `EUREKA_NPM_METADATA_MAX_DIST_TAGS=20`, `EUREKA_NPM_METADATA_TIMEOUT_MS=5000`, `EUREKA_NPM_METADATA_RATE_LIMIT_QPS=<operator-defined>`, `EUREKA_NPM_METADATA_USER_AGENT=<operator-defined>`, `EUREKA_NPM_METADATA_CONTACT=<operator-defined>`, `EUREKA_NPM_METADATA_PACKAGE_IDENTITY_REVIEW_REQUIRED=1`, `EUREKA_NPM_METADATA_SCOPED_PACKAGE_REVIEW_REQUIRED=1`, `EUREKA_NPM_METADATA_DEPENDENCY_RESOLUTION=0`, `EUREKA_NPM_METADATA_PACKAGE_DOWNLOAD=0`, `EUREKA_NPM_METADATA_TARBALL_DOWNLOAD=0`, `EUREKA_NPM_METADATA_PACKAGE_INSTALL=0`, `EUREKA_NPM_METADATA_ARCHIVE_INSPECTION=0`, `EUREKA_NPM_METADATA_LIFECYCLE_SCRIPT_EXECUTION=0`, `EUREKA_NPM_METADATA_NPM_AUDIT=0`, `EUREKA_NPM_METADATA_CACHE_REQUIRED=1`, and `EUREKA_NPM_METADATA_PUBLIC_SEARCH_FANOUT=0`.
