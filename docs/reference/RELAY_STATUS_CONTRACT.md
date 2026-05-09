# Relay Status Contract

`contracts/relay/relay_status.v0.json` exposes relay posture to clients.

The status must show `localhost_only: true`, `read_only: true`, and false values
for live access, source sync, downloads, uploads, accounts, telemetry, and
action execution.

Status is descriptive. It is not a hosting claim and does not imply a server
started by default.

