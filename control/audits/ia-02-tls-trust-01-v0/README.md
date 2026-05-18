# IA-02 TLS Trust Audit

IA-02-TLS-TRUST-01 diagnosed the local Python TLS trust failure that blocked
the approved IA metadata probe.

The diagnostic used Python's default verified SSL context. TLS verification
remained enabled, hostname checking remained enabled, and no insecure context or
custom bypass was used.

Result: the local Python trust store cannot complete a verified TLS handshake to
`archive.org`. The default OpenSSL CA file/capath are not present on this
machine, `certifi` is not available, and the handshake reports a self-signed
certificate chain. The approved IA live probe was not rerun.

IA-03 remains blocked.
