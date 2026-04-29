# Native Client Contract

Native Client Contract v0 defines future Windows, macOS, and other desktop
client responsibilities. It is contract and design work only. It does not
create a Visual Studio project, Xcode project, native GUI, FFI layer, installer
automation, package-manager behavior, native snapshot reader runtime, relay, or
download/execution automation.

Native clients are future super-clients, not website wrappers. They may
eventually browse/search, inspect evidence, open static snapshots, display
provenance, verify checksums, keep a local cache, integrate with a relay, and
hand off to package managers or installers after separate policy exists.

There are no implemented native GUI clients in v0. CLI remains the only current
local native-like surface.

This contract does not create a Visual Studio project. This contract does not create a native GUI. CLI remains the only current local native-like surface.

## Current CLI Versus Future GUI Clients

The current CLI under `surfaces/native/cli/` is a local, stdlib, native-like
surface over governed public/gateway boundaries. It is not a packaged desktop
application, not a native SDK, not a relay sidecar, and not a GUI client.

Future GUI clients must consume governed contracts:

- static public data under `public_site/data/`
- Signed Snapshot Format v0 and Signed Snapshot Consumer Contract v0
- Live Backend Handoff Contract v0 when a hosted backend later exists
- Relay Surface Design v0 only after relay prototype planning
- client profile and surface capability inventories

They must not import engine internals as their normal path or become an
alternative truth engine.

## Allowed Future Consumption

Future native clients may consume:

- static public data summaries
- static snapshot manifests and summaries
- checksums and future signature metadata
- source, eval, route, page, evidence, absence, and comparison summaries
- future live backend responses only when capability flags enable them
- future relay projections only with operator signoff

Public data and snapshots are static inputs, not a production live API. Native
clients must display status, limitations, source posture, and non-production
labels honestly.

## Snapshot Consumption

Native snapshot consumers must follow
`docs/reference/SNAPSHOT_CONSUMER_CONTRACT.md`.

At minimum, they must:

- read `README_FIRST.txt`
- parse `SNAPSHOT_MANIFEST.json`
- read `CHECKSUMS.SHA256`
- treat v0 signatures as placeholders
- verify SHA-256 checksums where supported
- warn when checksum verification is unavailable
- avoid live backend, live probes, JavaScript, login, or private state

Native clients must not claim production authenticity until real signing,
release provenance, public-key distribution, revocation/rotation, and consumer
signature-verification tests exist.

## Evidence And Provenance Display

Native clients may present evidence, source labels, source families, result
lanes, user-cost hints, compatibility evidence, absence notes, and comparison
results. They may change layout, but they must not rewrite resolver truth,
merge uncertain identities, hide placeholder source status, or convert
unknowns into positives.

## Local Cache Policy

Local cache is future policy work. A future cache may store public data,
snapshot validation results, and user-selected public artifacts only after
privacy and storage policy exists.

Private data is disabled by default. Native clients must not collect private
user history, private local paths, account/session data, or telemetry without a
separate explicit policy and operator/user consent.

## Handoff And Install Policy

Native clients may eventually hand off to:

- a system file opener
- a package manager
- an installer
- a restore/import workflow

Those actions are prohibited until Native Action / Download / Install Policy v0
or a successor exists. v0 native clients must not download executable
artifacts, run installers, mutate package managers, restore system state, or
claim executable trust.

## Relay Integration

Relay integration is future and optional. A native client may later host or
control a relay sidecar only after relay prototype planning, security/privacy
review, operator controls, and rollback procedures exist.

No native sidecar, socket listener, protocol bridge, FTP/SMB/WebDAV/NFS/Gopher
service, or local HTTP relay is implemented by this contract.

## Rust And Python Boundary

Python remains the active reference/oracle lane. Rust remains isolated parity
or planning only and is not a native SDK, FFI layer, production backend, or
runtime replacement.

Future native clients may consume Rust libraries only after a separate runtime
architecture decision. Native Client Contract v0 wires no Rust into native
clients.

## Versioning Expectations

Native clients must check schema/version fields before interpreting data. If a
snapshot, public data file, or live backend response is unsupported, the client
must show an explicit unsupported-version state instead of guessing.

## Not Implemented

Native Client Contract v0 does not implement:

- Visual Studio projects
- Xcode projects
- `.sln`, `.vcxproj`, `.csproj`, `.xcodeproj`, or `.pbxproj` files
- native GUI clients
- FFI
- Rust runtime wiring
- native snapshot reader runtime
- relay runtime or native sidecar
- installer automation
- package-manager behavior
- executable download or execution automation
- production signing or real signing keys
- live probes or external API calls
- production readiness
