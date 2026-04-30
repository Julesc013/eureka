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

- static public data under `site/dist/data/`
- Public Search Result Card Contract v0 after a future public search runtime
  exists
- Signed Snapshot Format v0 and Signed Snapshot Consumer Contract v0
- Live Backend Handoff Contract v0 when a hosted backend later exists
- Relay Surface Design v0 only after relay prototype planning
- client profile and surface capability inventories

They must not import engine internals as their normal path or become an
alternative truth engine.

## Allowed Future Consumption

Future native clients may consume:

- static public data summaries
- future public search result cards as governed by
  `docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`
- static snapshot manifests and summaries
- checksums and future signature metadata
- source, eval, route, page, evidence, absence, and comparison summaries
- future reviewed index-pack coverage and record-summary metadata, without raw
  SQLite databases or local cache export
- future reviewed contribution-pack summaries, without upload/import authority,
  private cache export, accounts, or automatic acceptance
- future master-index review queue outputs only after governed acceptance,
  without queue runtime, upload/import behavior, or native moderation features
- future live backend responses only when capability flags enable them
- future relay projections only with operator signoff

Public data and snapshots are static inputs, not a production live API. Native
clients must display status, limitations, source posture, and non-production
labels honestly.

Native clients must also follow
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md`. Public JSON is not a
production API; only named `stable_draft` field paths should drive durable
client behavior. Experimental fields may be displayed with version checks, and
volatile/internal fields must not become native-client compatibility promises.

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

Native Local Cache / Privacy Policy v0 now defines the future privacy and cache
contract. A future cache may store public data, snapshot validation results,
and user-selected public artifacts only after implementation review. Private
cache remains explicit opt-in future work.

Private data is disabled by default. Native clients must not collect private
user history, private local paths, account/session data, telemetry, diagnostics
uploads, source credentials, or cloud sync without separate explicit policy and
user consent. Native clients must not scan local archives or private user
folders by default.

## Project Readiness Review

Native Client Project Readiness Review v0 records that the repo is ready for a
minimal `windows_7_x64_winforms_net48` skeleton only after explicit human
approval. That decision is not an implementation approval. It requires a future
planning milestone to choose project path, namespace, build-host assumptions,
minimum read-only screens, and validation strategy before any Visual Studio or
Xcode project file is created.

## Handoff And Install Policy

Native clients may eventually hand off to:

- a system file opener
- a package manager
- an installer
- a restore/import workflow

Those actions are prohibited until Native Action / Download / Install Policy v0
or a successor exists. That policy now defines safe read-only actions, bounded
local fixture/manifest actions, future gated downloads and handoffs, executable
risk warnings, rights/access labels, and user-confirmation requirements. v0
native clients must not download executable artifacts, run installers, mutate
package managers, restore system state, claim executable trust, claim malware
safety, or claim rights clearance.

## Relay Integration

Relay integration is future and optional. A native client may later host or
control a relay sidecar only after relay prototype planning, explicit
implementation approval, security/privacy review, operator controls, and
rollback procedures exist.

No native sidecar, socket listener, protocol bridge, FTP/SMB/WebDAV/NFS/Gopher
service, or local HTTP relay is implemented by this contract.

Relay Prototype Planning v0 selects a future local static HTTP prototype shape,
but that plan does not implement or approve native sidecar behavior. Native
clients must continue treating relay integration as deferred.

## Rust And Python Boundary

Python remains the active reference/oracle lane. Rust remains isolated parity
or planning only and is not a native SDK, FFI layer, production backend, or
runtime replacement.

Future native clients may consume Rust libraries only after a separate runtime
architecture decision. Native Client Contract v0 wires no Rust into native
clients.

## Future Pack Import

Source/Evidence/Index Pack Import Planning v0 says future native clients may
only stage validated packs into private local quarantine after validate-only
tooling exists. Native clients must not scan arbitrary directories, expose
private staged packs through public surfaces, mutate local public search by
default, or submit staged packs to a master index without separate review.

AI Provider Contract v0 says future native clients may describe local or native
model providers only as disabled-by-default manifests until a separate runtime
milestone exists. Native clients must not send private data to model providers,
store credentials, log prompts, enable telemetry, or treat AI output as truth
without explicit future policy and review.

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
