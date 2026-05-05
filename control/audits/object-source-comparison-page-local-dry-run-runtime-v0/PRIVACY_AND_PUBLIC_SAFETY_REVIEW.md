# Privacy And Public Safety Review

P103 requires:

- No private paths.
- No secrets.
- No tokens.
- No IP, account, session, or user identifiers.
- No private URLs.
- No raw payload dumps.
- No executable payloads.
- No raw private query data.
- Synthetic public-safe examples only.
- Suspicious page fields are rejected or flagged.
- Dry-run output is not published.

The policy scanner rejects URL-like values, private path patterns, raw payload
fields, secret-like fields, and unsafe action claims.
