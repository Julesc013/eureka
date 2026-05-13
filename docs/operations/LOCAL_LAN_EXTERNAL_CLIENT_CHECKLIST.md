# Local LAN External Client Checklist

External-client smoke is preferred when a second local network device is
available. It is required before making any full LAN operational claim.

Record:

- client device type
- client network scope
- tested read-only routes
- mutation block checks
- timestamp

Private IP addresses may be redacted. Do not record precise private network
topology.

If no second device is available, record `external_client_smoke_performed:
false` with a reason. That is acceptable for LOCAL-12 pass-with-warnings, but it
is not cross-device proof.
