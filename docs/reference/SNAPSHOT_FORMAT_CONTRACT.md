# Snapshot Format Contract

Signed Snapshot Format v0 defines Eureka's first offline/static snapshot shape.
It is a contract and tiny seed example, not a production signed release.

## Purpose

A Eureka snapshot is a deterministic static directory that packages selected
public data summaries and snapshot manifests for offline inspection. It is for
future old clients, file-tree readers, relay designs, and native clients that
need a static copy of public publication-plane facts.

Snapshots are not the live backend. They cannot perform search, live probes,
auth, accounts, mutation, crawling, or dynamic source access.

Snapshots are also not `public_site/`. `public_site/` is the current GitHub
Pages static artifact. A snapshot is a future/offline export format derived
from governed public data and publication inventory.

## Versioning

- Format version: `0.1.0`
- Current status: experimental seed format
- Current example root: `snapshots/examples/static_snapshot_v0/`
- Current public `/snapshots/` route status: future/deferred

## Required Files

Every v0 snapshot must contain:

- `README_FIRST.txt`
- `index.html`
- `index.txt`
- `SNAPSHOT_MANIFEST.json`
- `BUILD_MANIFEST.json`
- `SOURCE_SUMMARY.json`
- `EVAL_SUMMARY.json`
- `ROUTE_SUMMARY.json`
- `PAGE_REGISTRY.json`
- `CHECKSUMS.SHA256`
- `SIGNATURES.README.txt`

Optional explanatory files may live under `data/`, `docs/`, or `demo/`, but v0
does not define executable payloads or binary mirrors. No executable downloads
are included in the v0 seed example.

## Checksums

`CHECKSUMS.SHA256` uses lowercase SHA-256 hex digests and relative paths. It
covers all committed seed snapshot files except `CHECKSUMS.SHA256` itself.

Checksums help detect accidental corruption and local drift. A checksum file
delivered over the same untrusted channel is not a complete authenticity proof.

## Signatures

v0 uses signature-placeholder documentation only. `SIGNATURES.README.txt`
explains that no production signing is performed, no real signing keys or
private keys are stored in the repo, and no production trust chain exists.

Future real signed snapshots require a separate key-management decision,
operator signing process, release provenance policy, and rotation/revocation
policy.

## Included Data

The v0 seed example includes deterministic copies or projections of:

- `public_site/data/source_summary.json`
- `public_site/data/eval_summary.json`
- `public_site/data/route_summary.json`
- `public_site/data/page_registry.json`
- `public_site/data/build_manifest.json`

The snapshot may reference publication inventory as source input, but it must
not include local absolute paths, secrets, caches, databases, or private stores.

## Exclusions

The v0 format explicitly excludes:

- real private signing keys
- production signatures
- executable downloads
- real software binaries
- live backend responses
- live probe results
- Internet Archive live calls
- Google scraping or automated external search output
- arbitrary local filesystem ingestion
- external baseline observations unless a human commits governed evidence

## Clients

Old clients should treat snapshots as read-only public data. Relay Surface
Design v0 now defines the future relay policy that may later consume production
snapshots, but no relay runtime exists. Future relay and native clients may
consume snapshots only after their own operator/security and client-readiness
policies are accepted.

No login or private user data may be layered onto insecure compatibility
snapshot transports.
