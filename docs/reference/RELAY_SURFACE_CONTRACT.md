# Relay Surface Contract

Relay surfaces are future/deferred. No local LAN relay, FTP bridge, SMB bridge,
WebDAV bridge, protocol proxy, or old-system gateway is implemented.

A future relay may project governed static data or snapshots to clients that
cannot consume the normal static web surface. Before that work starts, Eureka
needs a separate operator/security contract covering:

- explicit local operator enablement
- read-only public data defaults
- no open relay behavior
- no private local path exposure
- no auth/private account data
- no live probes by default
- disable/rollback controls
- network binding and LAN exposure rules

Relay trust must come from signed manifests/checksums later, not from insecure
transport. Relay behavior must not bypass publication contracts.
