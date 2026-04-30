# Relay Surface

Relay Surface Design v0 defines a future local relay architecture for old,
weak, offline, or protocol-limited clients. It is design, contract, inventory,
validation, and operator-policy work only.

No relay runtime is implemented. No network listeners, protocol servers, FTP,
SMB, AFP, WebDAV, NFS, Gopher, proxying, protocol translation, local HTTP
relay, native sidecar, or socket-opening behavior is added by this milestone.

## Purpose

The future relay would be an operator-controlled local or LAN bridge. It may
eventually let old clients consume public Eureka data through simpler
projections when they cannot use modern browser, TLS, or API surfaces.

The relay exists to solve compatibility, not truth. It must not rewrite
resolver meaning, rank evidence differently, or become a trust oracle. Modern
resolver truth still comes from governed source/evidence records, public data
summaries, static snapshots, and future live backend contracts.

## Placement Options

A future relay may run on:

- a modern desktop
- a home server or NAS
- a Raspberry Pi-class machine
- a trusted LAN host
- a native client sidecar

All placements require a later implementation milestone, operator signoff, and
security review before any process listens on a port or exports a filesystem
view.

## Data Relationship

The relay should consume existing governed projections before it consumes any
live backend:

- `site/dist/data/` for static public JSON summaries
- `site/dist/lite/` for old-browser HTML shape
- `site/dist/text/` for plain text output
- `site/dist/files/` for file-tree manifests and checksums
- `snapshots/examples/static_snapshot_v0/` as the current seed snapshot format
- Signed Snapshot Consumer Contract v0 for future snapshot read order,
  checksum checks, missing optional file behavior, and v0 signature-placeholder
  limits
- future production snapshots only after signing/key policy exists
- future `/api/v1` responses only after live backend handoff policy enables
  them

The relay should not import engine internals or create a separate truth model.

Native Local Cache / Privacy Policy v0 keeps future relay projections
public/read-only by default. A relay must not expose private cache, private
local paths, credentials, user history, diagnostics, telemetry, account/session
state, or private uploads to old or insecure clients by default.

## Future Protocol Candidates

Future protocol candidates are recorded in
`control/inventory/publication/relay_surface.json` and remain deferred:

- local static HTTP projection
- local text HTTP projection
- local file-tree HTTP projection
- read-only FTP-style mirror
- read-only WebDAV projection
- read-only SMB projection
- read-only AFP projection
- read-only NFS projection
- experimental Gopher-style projection
- native client sidecar
- snapshot mount or browse root

These are candidates, not implemented transports.

Relay Prototype Planning v0 selects local static HTTP as the first future
prototype candidate. That decision is planning only: the future prototype would
be localhost-only by default, read-only, and limited to allowlisted static
public data plus seed snapshot files. No relay server, local HTTP relay,
socket listener, protocol server, native sidecar, snapshot mount, private file
serving, live backend proxy, live probe, or runtime path exists now.

## Safety Invariants

- Local or trusted LAN by default.
- Read-only by default.
- Public data only by default.
- Private data disabled by default.
- Write actions disabled by default.
- Live probes disabled by default.
- Admin routes disabled for old clients.
- No credentials, sessions, account state, or private history over insecure
  transports.
- No installer execution or executable mirror behavior.
- No download, install, execute, restore, uninstall, rollback, private upload,
  malware-scanning, or rights-clearance claim.
- Integrity should come from manifests, checksums, and future signatures, not
  from insecure transport.

## Relationship To Other Surfaces

The relay is downstream from the compatibility surface strategy. Old clients
should first degrade through static site, lite HTML, text, files, and future
snapshots. Relay is a later bridge for environments that need a local host to
translate access patterns.

The relay is also downstream from the live backend handoff and live probe
gateway contracts. It must not expose live search or live probing unless future
operator policy explicitly enables those capabilities.

The relay is downstream from Native Action / Download / Install Policy v0 as
well. It may eventually project action metadata, but old or insecure relay
clients must not receive download, mirror, install handoff, package-manager
handoff, execute, restore, uninstall, rollback, private upload, write/admin, or
live-probe controls.

## Implementation Boundary

Relay Surface Design v0 prepares future Relay Prototype v0 and Native Client
Contract v0. Signed Snapshot Consumer Contract v0 prepares the snapshot
consumption side of that future relay without creating the relay. This does not
implement a relay server, open sockets, expose private data, enable write/admin
paths, add protocol libraries, or claim old-client support beyond the existing
static seed surfaces.

Native Client Contract v0 now records the future native side of relay
integration. It does not create a native sidecar, GUI project, FFI layer,
installer automation, download/execution automation, relay runtime, or Rust
runtime wiring.

Relay Prototype Planning v0 records the first implementation-ready plan for a
future local static HTTP prototype. It requires explicit human approval before
implementation and keeps LAN exposure, private data, writes, live backend
proxying, live probes, downloads, installers, telemetry, and executable launch
out of the initial scope.
