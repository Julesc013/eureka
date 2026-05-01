# Privacy And Redaction Policy

Raw query retention default is `none`.

Public-safe candidate records must not include:

- IP address
- account ID
- email
- phone number
- API key
- auth token
- password
- private key
- private path
- private URL
- local result identifier
- executable payload
- raw copyrighted payload dump

If prohibited data is detected, a candidate record must be rejected or redacted
before aggregate use. Individual candidate records are not publishable by
default.
