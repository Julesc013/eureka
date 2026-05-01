# Query Privacy And Redaction Policy

Status: P59-P64 contract policy only.

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

The same prohibited data categories apply to shared query/result cache entries,
cache keys, cached result summaries, absence/gap summaries, and search miss
ledger entries. P62 extends the same prohibited data posture to search need
record examples and future search need aggregates. P63 extends it to probe
queue items and future probe aggregate summaries. P64 extends it to candidate
index records, candidate identity fingerprints, evidence refs, source refs,
conflict summaries, and future candidate public aggregate summaries.

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

P60 adds a shared query/result cache contract only. It keeps raw query retention
default `none`, does not add runtime cache writes, and does not make cache
entries publishable by default.

P61 adds a search miss ledger contract only. It keeps raw query retention
default `none`, requires scoped absence instead of broad absence claims, and
does not add runtime ledger writes, telemetry, search need creation, probe
enqueueing, result-cache mutation, candidate-index mutation, local-index
mutation, or master-index mutation.

P62 adds a search need record contract only. It keeps raw query retention
default `none`, adds no runtime need store, no telemetry, no public query
logging, no demand-count runtime, no probe enqueueing, no candidate-index
mutation, no result-cache mutation, no miss-ledger mutation, no local-index
mutation, and no master-index mutation.

P63 adds a probe queue contract only. It keeps raw query retention default
`none`, adds no runtime probe queue, no persistent probe queue, no telemetry, no
public query logging, no probe execution, no live source call, no source cache
mutation, no evidence ledger mutation, no candidate-index mutation, no
search-need mutation, no result-cache mutation, no miss-ledger mutation, no
local-index mutation, and no master-index mutation.

P64 adds a candidate index contract only. It keeps raw query retention default
`none`, adds no runtime candidate index, no persistent candidate index, no
candidate promotion runtime, no public search candidate injection, no telemetry,
no source cache mutation, no evidence ledger mutation, no probe queue mutation,
no search-need mutation, no result-cache mutation, no miss-ledger mutation, no
local-index mutation, and no master-index mutation.
