# Pack Input And Trust Model

Allowed future pack origins:

- repo canonical examples
- local operator-provided pack path after explicit approval
- signed maintainer pack future
- reviewed institutional pack future
- community contribution pack future after public contribution contract

Forbidden origins for v0 runtime:

- public upload endpoint
- arbitrary URL
- untrusted web download
- private cache root
- arbitrary local filesystem tree
- executable installer
- package manager output
- live connector response
- raw user telemetry

Trust rules:

- pack claims are untrusted until validated
- validation is structural, not truth acceptance
- provenance must be preserved
- source/evidence/candidate promotion remains separate
- invalid packs are rejected or quarantined
- pack secrets/private paths cause rejection or redaction according to policy
