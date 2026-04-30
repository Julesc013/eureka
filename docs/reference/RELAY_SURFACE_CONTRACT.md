# Relay Surface Contract

Relay Surface Design v0 is implemented as a design contract only. The relay
surface remains future/deferred in the publication matrices.

No relay runtime, local LAN relay, FTP bridge, SMB bridge, AFP bridge, WebDAV
bridge, NFS export, Gopher projection, protocol proxy, protocol translation, or
old-system gateway is implemented.

## Status Taxonomy

Relay records use these statuses:

- `design_only`: contract, inventory, documentation, and validation exist.
- `future_deferred`: candidate behavior is accepted for later review but is not
  implemented.
- `implemented_static_input`: static data exists and may be consumed by future
  relay work.
- `future_disabled`: candidate live or private input remains disabled pending
  later policy.

## Future Inputs

A future relay may consume:

- public data summaries from `site/dist/data/`
- lite HTML from `site/dist/lite/`
- plain text from `site/dist/text/`
- file-tree manifests and checksums from `site/dist/files/`
- future public search result cards after a later runtime emits them under
  Public Search Result Card Contract v0
- static snapshot manifests and checksums
- route, source, eval, and page summaries
- future live backend responses only after capability flags and handoff policy
  permit them

The relay must not ingest arbitrary local filesystem roots by default, and it
must not treat private local cache content as public data without a separate
operator policy.

Future relay consumers of generated public data must follow
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md`. Stable-draft field paths may
be projected read-only after explicit implementation approval; experimental,
volatile, and internal fields must not become relay protocol promises or
old-client compatibility guarantees.

Signed Snapshot Consumer Contract v0 now defines the future snapshot read
order, checksum posture, and v0 signature-placeholder handling that any relay
snapshot projection must follow. No relay snapshot consumer is implemented.

Public Search Result Card Contract v0 defines a future card shape that relay
clients may project read-only. It does not implement a relay search endpoint,
live backend proxy, download surface, install handoff, upload behavior, or
runtime relay service.

Relay Prototype Planning v0 chooses the first future relay prototype shape:
`local_static_http_relay_prototype`. It may consume only allowlisted static
public data, text/files seed surfaces, and seed snapshot files if a later
human-approved implementation milestone exists. It must not consume arbitrary
user directories, private cache roots, credentials, live API responses, live
probe outputs, or external URLs.

## Future Outputs

Possible future relay outputs are projections of the same resolver truth:

- simple HTML
- plain text
- file-tree indexes
- manifest and checksum views
- optional protocol projections for old clients
- optional native sidecar views after native-client contracts exist

Output modes must preserve source/evidence/status meaning. They may simplify
presentation and transport, but they must not rewrite the answer.

## Safety Invariants

- Relay is local or trusted-LAN by default.
- Relay is read-only by default.
- Public data is the only default data class.
- Private user data is disabled by default.
- Write actions are disabled by default.
- Live probes are disabled by default.
- Admin routes are disabled for old clients.
- Insecure transports can carry only public/read-only data.
- Integrity depends on manifests, checksums, and future signatures.
- Relay is not a trust oracle.

## Modern Secure Host Requirement

The following must require a modern secure host, explicit user/operator
approval, or both before any future implementation:

- private data exposure
- local cache exposure
- write actions
- admin controls
- live backend use
- live source probes
- credentials or account/session data
- any executable handoff

The following must never be exposed through insecure old-client surfaces:

- account credentials
- private user history
- write/admin endpoints
- arbitrary local filesystem paths
- private caches by default
- live probe controls
- installer execution controls
- executable download, mirror, package-manager handoff, or restore controls

Native Action / Download / Install Policy v0 applies to future relay work. A
relay may project read-only metadata, text, manifests, checksums, and snapshot
summaries, but it must not expose download, install, execute, mirror, private
upload, write/admin, or live-probe behavior to old or insecure clients.

Relay Prototype Planning v0 limits the first future outputs to read-only HTTP
pages, plain text pages, JSON static summaries, file-tree index views, checksum
files, and snapshot manifest views. Write endpoints, uploads, admin endpoints,
live probe endpoints, live backend proxy routes, arbitrary file serving,
private path display, credential display, telemetry endpoints, and executable
launch remain prohibited.

## Versioning

The v0 relay contract is experimental. Future implementations must keep the
inventory record versioned and must add tests before a protocol candidate moves
from `future_deferred` to any implemented status.
