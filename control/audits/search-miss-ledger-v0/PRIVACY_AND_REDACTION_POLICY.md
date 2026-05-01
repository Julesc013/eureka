# Privacy And Redaction Policy

Raw query retention default is `none`.

Public-safe miss entries must not contain IP address, account ID, email, phone
number, API key, auth token, password, private key, private path, private URL,
private local result identifier, user-uploaded filename without consent, or
unsafe raw query text.

If sensitive material is detected, an entry must be rejected by the privacy
filter or marked redacted before it can be considered for aggregate learning.

