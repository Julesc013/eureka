# Relay Security And Privacy

Relay Surface Design v0 is future-only. It does not implement relay runtime,
network listeners, protocol servers, private data exposure, write paths, or live
source probes.

## Default Posture

- No public internet exposure by default.
- Local or trusted-LAN scope only for any future v0 prototype.
- Read-only by default.
- Public data only by default.
- No credentials to old clients.
- No private local paths by default.
- No private user history by default.
- No private cache or diagnostics data to old clients by default.
- No account or session data over insecure transports.
- No telemetry or analytics through relay surfaces by default.
- No write or admin endpoints to old clients.
- No installer execution over relay in v0.
- No live source probing through relay unless a future policy explicitly
  permits it.

## Insecure Transport Warning

Old-client transports may lack modern TLS, authentication, or permission
models. If a future relay uses those transports, they can carry only public
read-only data. They must not carry credentials, private cache, private local
paths, user history, diagnostics, account/session state, write controls,
telemetry controls, or live probe controls.

Checksums can detect accidental corruption. Checksums delivered over the same
untrusted channel are not full authenticity proof. Future signature policy and
operator trust decisions are required before authenticity claims are made.

## Future Threat Model

Before implementation, a relay prototype needs a threat model covering:

- bind addresses and LAN exposure
- firewall assumptions
- protocol-specific permissions
- read-only enforcement
- private-data exclusion
- local cache and private path exclusion
- log content and retention
- snapshot verification
- disable and rollback procedure
- source/live-backend capability gates
- old-client credential and session risks

No implementation should proceed until that review is committed and validated.
