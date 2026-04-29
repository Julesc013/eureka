# Public Data Stability Policy

Public Data Contract Stability Review v0 defines field-level stability classes
for generated static public JSON under `public_site/data/`.

This policy does not make public JSON a production API. Eureka remains
pre-product and public-alpha/non-production.

No current public JSON file is production-stable.

## Stability Classes

`stable_draft`

Pre-alpha field path that cautious static clients, snapshot consumers, future
relay planning, and future native planning may consume with `schema_version`
checks. Removing, renaming, or changing the type of a `stable_draft` field
requires a breaking-change note.

`experimental`

Display-only or version-pinned field path. Clients may show it, but should not
branch durable behavior on it unless they pin to a known schema version and are
prepared for change.

`volatile`

Diagnostic count, provenance value, text, or audit detail that may change
between generated artifacts. Clients should not depend on exact values.

`internal`

Repo path, source input, generator command, or implementation detail. These
fields are useful for audits and validators but are not public client API.

`deprecated`

Documented field retained during a migration window. No current generated
public data field is deprecated.

`future`

Reserved field or surface posture for later contracts. A future field does not
imply current implementation.

## Breaking Changes

A breaking-change note is required before removing, renaming, or changing the
type of a `stable_draft` field. Changing a disabled no-live/no-deployment/no
download/no-telemetry safety flag to an enabled posture requires a separate
enabling contract and implementation evidence.

Adding fields is non-breaking. Moving count values as inventories, evals, or
audits change is non-breaking. Changing limitation text is non-breaking unless a
later consumer contract says otherwise.

## Client Guidance

Clients must:

- check `schema_version`
- treat unknown fields as ignorable
- show limitations and disabled/future posture honestly
- avoid production API claims
- avoid treating internal repo paths as public API
- avoid treating experimental source capability booleans as finalized connector
  contracts

Snapshots, relay prototypes, and native clients must use this policy alongside
their own contracts. This review does not implement snapshot readers, relay
runtime, native clients, live APIs, live probes, downloads, installers,
telemetry, accounts, production signing, or deployment behavior.
