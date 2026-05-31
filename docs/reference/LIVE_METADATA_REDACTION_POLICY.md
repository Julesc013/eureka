# Live Metadata Redaction Policy

Committed pilot artifacts may contain only public-safe summaries.

Allowed:

- request plan identifiers
- query identifiers
- endpoint class names
- source family names
- status labels
- counts
- hashed identifiers
- candidate summaries marked review-only

Forbidden:

- raw HTTP response bodies
- raw full live source logs
- downloads
- extracted files
- install or execution outputs
- secrets or provider credentials

Redaction does not make a candidate true. Review remains required.
