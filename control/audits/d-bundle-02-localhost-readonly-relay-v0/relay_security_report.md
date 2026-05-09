# Relay Security Report

The relay security policy is loopback-only and read-only. `0.0.0.0`, `::`, `*`,
and public wildcard binds are rejected.

No secrets, cookies, credentials, account sessions, public write CORS behavior,
or telemetry are introduced.

