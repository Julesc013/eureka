# Public Alpha Environment

The read-only public alpha uses non-secret environment configuration.

| Variable | Required | Meaning |
| --- | --- | --- |
| `EUREKA_ALPHA_SNAPSHOT_MANIFEST` | yes | Path or identifier for the reviewed snapshot manifest |
| `EUREKA_ALPHA_RELAY_MANIFEST` | yes | Path or identifier for the relay manifest |
| `EUREKA_ALPHA_ENVIRONMENT` | yes | `local_preview`, `static_snapshot`, or future approved environment name |
| `EUREKA_ALPHA_READ_ONLY` | yes | Must be true for public alpha |
| `EUREKA_ALPHA_BASE_URL` | no | Public base URL, only after future deployment approval |
| `EUREKA_ALPHA_RATE_LIMIT_PROFILE` | no | Rate-limit profile name |
| `EUREKA_ALPHA_LOG_REDACTION_PROFILE` | no | Redaction profile name |

No provider credentials, operator tokens, account secrets, source credentials, or
deployment credentials are required or allowed in the repository for this
baseline.
