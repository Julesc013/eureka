# Privacy And Redaction Policy

Raw query retention defaults to `none`.

Public-safe probe queue examples must not contain private paths, private URLs,
IP addresses, account IDs, user identifiers, sensitive tokens, local result IDs,
unsafe raw queries, executable payloads, or raw copyrighted payload dumps.

If sensitive material is detected, a future item must be rejected or redacted
before aggregate learning.
