# Redaction Review

The inspector applies conservative redaction to projected output:

- Windows private paths such as `C:\Users\...`
- POSIX home paths such as `/home/...` and `/Users/...`
- temporary private path patterns
- secret-like values such as `sk-...`
- private-key blocks
- values under secret-like field names such as `api_key`, `auth_token`,
  `password`, `private_key`, and `secret`

Committed examples are synthetic and should not contain such values, but the
redaction layer protects diagnostic inspection of explicit local manifests.

Redaction does not authorize public export. Local/private staging manifests
remain local/private by default.
