# Failure And Error Model

Bounded failures include:

- invalid JSON
- missing result set
- missing result ID
- unsupported factor field
- private path detected
- URL or live source parameter rejected
- secret-like field detected
- telemetry, user-profile, ad, popularity, or model signal detected
- suppression claim detected
- mutation claim detected
- explanation missing
- output path rejected
- strict-mode failure
- non-strict current-order fallback

Errors must not include private payload dumps.

