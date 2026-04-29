# Relay Operator Checklist

Status: future/unsigned. This checklist is planning material only. There is no
relay runtime to run yet.

Relay Prototype Planning v0 records `local_static_http_relay_prototype` as the
first future prototype candidate. That plan is not implementation approval. A
future implementation still requires explicit human approval and an approved
localhost-only/read-only/static scope.

Operator signoff:

- operator:
- date:
- host:
- approved protocols:
- rollback owner:

Future checklist:

- choose the local host
- choose local-only or trusted-LAN network scope; first prototype defaults to
  localhost-only
- choose allowed protocols
- choose snapshot or public-data root
- confirm read-only mode
- confirm public data only by default
- confirm no private data exposure
- confirm no private local paths
- confirm no write or admin endpoints for old clients
- confirm no credentials or account/session data to old clients
- confirm live probes remain disabled unless a future policy explicitly enables
  them
- confirm no executable mirror or installer execution behavior
- confirm logs and privacy posture
- confirm firewall or LAN-only posture
- confirm rollback or disable procedure
- confirm snapshot manifest/checksum/signature validation posture
- record signoff before any implementation milestone

This checklist does not configure a relay, start a process, open a socket, add
protocol support, expose private data, or approve production use.
