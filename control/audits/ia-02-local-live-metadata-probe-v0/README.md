# IA-02 Local Live Metadata Probe Audit

IA-02 added the bounded live-probe policy, transport, runtime, CLI, validator,
tests, and audit evidence for a metadata-only Internet Archive probe.

The approved live request was attempted once under policy. The local Python TLS
trust store rejected the connection with `ssl_certificate_verify_failed` before
an Internet Archive HTTP response was available. The result is recorded as
partial rather than promoted to IA-03.

No raw live response body was committed. No downloads, uploads, source-cache
writes, evidence writes, index mutation, extraction, model/provider calls,
deployment, production readiness claim, or public launch claim occurred.
