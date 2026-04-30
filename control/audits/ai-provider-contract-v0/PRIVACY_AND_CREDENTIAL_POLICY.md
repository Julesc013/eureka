# Privacy And Credential Policy

AI providers are disabled by default. Private data is disabled by default.
Telemetry and prompt/output logging are disabled by default.

Remote providers are future-only and require explicit credentials, consent, and
operator policy before any runtime exists. Provider manifests must not include
API keys, secrets, tokens, cookies, private keys, account state, or endpoint
secrets.

Local providers do not receive arbitrary filesystem access from a manifest.
Private local sources remain governed by local cache and pack-import policies.
