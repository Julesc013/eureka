# Relay Read-Only Security Policy

The D-BUNDLE-02 relay accepts GET-style handling only. POST, PUT, PATCH, and
DELETE are blocked. Admin, upload, download, execute, install, mirror, write,
and delete route families are blocked.

Only `127.0.0.1` and `localhost` are current allowed bind hosts. `0.0.0.0`, `::`,
`*`, and empty or public wildcard hosts are rejected.

No secrets, cookies, credentials, account sessions, public CORS write behavior,
or telemetry are used.

