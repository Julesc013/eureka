# Privacy And Redaction Policy

Raw query retention defaults to none. Public-safe examples set:

- `raw_query_retained: false`
- `raw_query_retention_class: not_retained`
- `raw_query_redacted: true`
- `safe_to_publish_raw_query: false`

Queries containing personal data, secrets, private paths, private URLs,
credentials, local identifiers, or user-uploaded filenames must be rejected or
redacted before any aggregate use. P59 does not publish individual observations.
