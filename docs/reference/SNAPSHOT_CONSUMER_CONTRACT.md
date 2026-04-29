# Snapshot Consumer Contract

Signed Snapshot Consumer Contract v0 defines how future consumers should read
and validate Eureka static snapshots. It is contract and design work only. It
does not implement a snapshot reader runtime, native client, relay, production
signing, key management, executable download surface, or live backend.

There is no production consumer in v0.

This contract does not implement a relay. This contract does not implement a native client.

## What Is A Snapshot Consumer?

A snapshot consumer is any future client or tool that reads a Eureka snapshot
directory instead of calling a live backend. Examples include:

- a minimal file-tree reader
- a plain text or text-browser reader
- a lite HTML reader for old browsers
- a future relay projection
- a future native client
- a future audit tool

Consumers preserve resolver truth from snapshot manifests and summaries. They
may change presentation, but they must not rewrite evidence, source posture,
eval status, route status, or limitations.

## Minimum Compliant Consumer

The minimum compliant consumer:

- reads `README_FIRST.txt` before making claims about the snapshot
- reads `SNAPSHOT_MANIFEST.json`
- reads `CHECKSUMS.SHA256`
- reads `SIGNATURES.README.txt`
- can present `index.txt` or an equivalent file-tree view
- does not require a live backend, live probes, JavaScript, accounts, or
  network access
- warns or fails closed when it cannot verify checksums
- states that v0 signatures are placeholders

It must not claim production authenticity, complete source coverage, real
signature verification, live backend availability, or snapshot consumption
being implemented in Eureka today.

## Full Future Consumer

A full future consumer should:

- verify every entry in `CHECKSUMS.SHA256`
- parse all required JSON manifests
- enforce `snapshot_format_version`
- render or expose `index.html` and `index.txt` when supported
- list sources from `SOURCE_SUMMARY.json`
- list eval/audit posture from `EVAL_SUMMARY.json`
- list route/publication status from `ROUTE_SUMMARY.json`
- list pages from `PAGE_REGISTRY.json`
- handle missing optional files with explicit notices
- surface signature-placeholder limitations
- reject unsupported future features with an explicit not-supported status

Real signature verification, release provenance checks, production snapshot
bundles, relay projection, and native client behavior require later contracts
and implementation milestones.

## Required Read Order

Consumers should read required files in this order:

1. `README_FIRST.txt`
2. `SNAPSHOT_MANIFEST.json`
3. `BUILD_MANIFEST.json`
4. `CHECKSUMS.SHA256`
5. `SOURCE_SUMMARY.json`
6. `EVAL_SUMMARY.json`
7. `ROUTE_SUMMARY.json`
8. `PAGE_REGISTRY.json`

After that, consumers may read `index.txt`, `index.html`, `data/README.txt`,
or optional explanatory files if they exist.

## Checksum Semantics

`CHECKSUMS.SHA256` is required. A compliant consumer with SHA-256 support must
verify each listed file and report missing, extra, or mismatched entries.

Checksums detect accidental corruption and local drift. Checksums delivered
through the same untrusted channel as the snapshot are not full authenticity
proof. A consumer that cannot compute SHA-256 must warn and must not claim
integrity or authenticity.

## Signature Placeholder Semantics

v0 signatures are placeholders. `SIGNATURES.README.txt` tells consumers where
future signature metadata will live, but it is not a real signature file.

Consumers must state:

- v0 signatures are placeholders
- no real signing keys are included
- no private keys are stored in the repo
- no production signing is performed
- no production trust chain exists

Future real signatures require key-management, public-key distribution,
release provenance, revocation/rotation, and consumer verification tests.

## Missing Optional Files

Optional files may be absent. Consumers should continue with a notice when
optional docs, demos, or extra indexes are missing. They must not fabricate
replacement data, fetch missing files from the network, or treat missing
optional files as proof that the required snapshot is corrupt.

Required files are different: a missing required file is a validation failure.

## Discovering Objects, Sources, Evals, And Routes

Consumers discover available data from required summaries:

- `SOURCE_SUMMARY.json` for source IDs, labels, families, coverage posture,
  placeholder status, and limitations
- `EVAL_SUMMARY.json` for archive eval and search usefulness posture
- `ROUTE_SUMMARY.json` for route/publication status
- `PAGE_REGISTRY.json` for static page registry entries
- `BUILD_MANIFEST.json` and `SNAPSHOT_MANIFEST.json` for snapshot provenance,
  file lists, limitation flags, and format version

Snapshots do not promise complete global coverage. Consumers must display
unknown, placeholder, capability-gap, source-gap, or pending-manual states
honestly.

When a snapshot includes generated public data copied from `public_site/data/`,
consumers must follow `docs/reference/PUBLIC_DATA_STABILITY_POLICY.md`.
Only `stable_draft` field paths are safe for cautious pre-alpha dependence;
experimental fields are display-only unless a consumer version-pins them.
This does not make public JSON or snapshots a production API.

## Old-Client Degradation

Old or weak clients should degrade by capability:

- file-tree clients read filenames, manifests, and checksums
- text clients prefer `index.txt` and text summaries
- lite HTML clients prefer `index.html`
- clients that cannot verify checksums must warn
- clients that cannot parse JSON should still show `README_FIRST.txt`,
  `index.txt`, and limitation text

Old clients must not require JavaScript, a live API, login, private user state,
or live source probes.

## Relay And Native Consumers

Future relay and native clients must use this same contract. Relay consumers
remain future/deferred and require separate relay prototype planning before any
network service, socket, protocol server, or LAN bridge exists.

Relay Prototype Planning v0 now records that the first future relay prototype
would consume seed snapshots only as read-only static files through an
allowlisted local static HTTP projection after explicit human approval. No
relay snapshot consumer, socket listener, snapshot mount, live backend proxy,
or live probe behavior is implemented.

Native consumers remain future/deferred and require Native Client Contract v0
before any native project, installer, sidecar, or packaged runtime exists.
Native Client Contract v0 now defines those future native lanes and confirms
that no native GUI client, Visual Studio/Xcode project, FFI, installer
automation, native snapshot reader runtime, relay sidecar, or Rust runtime
wiring exists.

Both future surfaces must treat snapshots as read-only public data by default
and must not expose private data, write/admin controls, executable downloads,
or live probes through snapshot consumption.

Native Action / Download / Install Policy v0 adds one more rule for snapshot
consumers: a snapshot may support inspect, preview, read, and checksum
verification, but snapshot presence is not permission to download, mirror,
install, execute, restore, or claim rights clearance or malware safety.

## Error Handling

Consumers should report clear statuses:

- `missing_required_file`
- `invalid_json`
- `checksum_mismatch`
- `checksum_unavailable`
- `unsupported_snapshot_format`
- `signature_placeholder_only`
- `optional_file_missing`
- `unsupported_feature`

Unsupported features should be explicit and non-fatal unless they affect a
required validation step.

## Version Compatibility

Consumers should read `snapshot_format_version` from
`SNAPSHOT_MANIFEST.json`. A consumer that does not support the version should
stop with `unsupported_snapshot_format` rather than guessing semantics.

The current seed format is `0.1.0` and experimental.

## Security Limitations

Snapshots are static public data. They do not contain private user data,
secrets, credentials, real signing keys, software binaries, executable
downloads, live backend output, live probe output, or automated external
observations.

Consumers must not use a snapshot as permission to fetch URLs, scrape external
sources, ingest arbitrary local filesystem roots, run installers, or expose
private paths.

Consumers must not treat a snapshot as private cache. Native Local Cache /
Privacy Policy v0 keeps snapshots public/offline and excludes private cache,
private local paths, credentials, telemetry, account data, diagnostics, and
private user history from snapshot contents.

## Not Implemented

This contract does not implement:

- a snapshot reader runtime
- a native client
- a relay
- FTP, SMB, WebDAV, NFS, Gopher, local HTTP relay, or protocol translation
- production signing
- real private keys or certificates
- executable/software downloads
- live backend routes
- live probes
- Internet Archive or Google access
