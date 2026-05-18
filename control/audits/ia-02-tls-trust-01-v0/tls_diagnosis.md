# TLS Diagnosis

The diagnostic script created a default Python SSL context with certificate
verification and hostname checking enabled, resolved `archive.org`, then
attempted a TLS handshake without fetching item, media, or metadata content.

Observed:

- default context created: true
- verify mode: `CERT_REQUIRED`
- hostname checking: true
- host resolution: true
- TLS handshake: fail
- failure type: `ssl_certificate_verify_failed`
- redacted failure: `self_signed_certificate_in_chain`
- insecure context used: false

The Python OpenSSL verify paths do not point to an existing CA file or CA
directory on this machine, and `certifi` is not available.
