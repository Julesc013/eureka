# Query Privacy And Redaction Policy

Status: P59 contract policy only.

Query observations must prevent unsafe raw user data from becoming public
evidence, telemetry, source truth, or master-index truth. Raw query retention
defaults to none.

## Prohibited Data

Public-safe query observations and examples must not contain:

- IP address
- account ID
- email
- phone number
- API key
- auth token
- password
- private key
- private path
- Windows absolute path
- POSIX home path
- private URL
- long raw query with personal data
- user-uploaded filenames without consent
- local index hit identifiers that expose private state

If any prohibited data is detected, the observation must be rejected by the
privacy filter or redacted before it can be considered for aggregate learning.
Individual observations are not public by default.

## Redaction Rules

- Keep `raw_query_retained` false by default.
- Keep `safe_to_publish_raw_query` false by default.
- Use normalized public-safe terms for aggregate learning.
- Use a non-reversible fingerprint for grouping.
- Mark `publishable` false unless a later policy explicitly allows individual
  publication.
- Mark `public_aggregate_allowed` false when sensitive material remains.

## Non-Goals

This policy does not implement telemetry, runtime persistence, query logs,
uploads, accounts, edge analytics, result-cache writes, miss-ledger writes,
probe enqueueing, candidate-index mutation, local-index mutation, or
master-index mutation.
