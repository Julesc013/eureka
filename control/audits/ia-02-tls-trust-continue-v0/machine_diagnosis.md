# Machine Diagnosis

The active Python executable uses OpenSSL 3.0.13. With no certificate
environment variables set, Python can resolve `archive.org` and create a
verified SSL context, but the verified handshake fails with:

- `ssl_certificate_verify_failed`
- `self_signed_certificate_in_chain`

The default OpenSSL CA file and directory are absent for this Python install,
and top-level `certifi` is not installed. Python's pip-vendored CA bundle is
available locally.

When `SSL_CERT_FILE` is set in the current shell to that existing local CA
bundle, the verified handshake succeeds. Local filesystem paths are redacted
from committed diagnostics.

