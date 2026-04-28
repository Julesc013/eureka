# Compatibility Surfaces

Compatibility Surface Strategy v0 governs how Eureka projects the same
resolver truth into multiple client shapes without pretending one modern app
can serve every client.

Invariant: same resolver truth, multiple projections. Static pages, text files,
file manifests, future snapshots, future relays, future native clients, and
future live API routes must all preserve the same source/evidence/status
meaning. They may differ in presentation and transport, not in truth.

This is strategy, contract, and inventory work only. Signed Snapshot Format v0
now adds a repo-local seed snapshot example, and Signed Snapshot Consumer
Contract v0 now defines future consumer read order and checksum/signature
handling, but no runtime product behavior, deployment, public `/snapshots/`
route, production signed snapshot release, snapshot reader runtime, relay
service, native client, live `/api/v1`, or live probe is implemented.

Compatibility Surface Strategy v0 does not implement new runtime product behavior.

## Surface Families

| Surface | Current status | Root or consumer | Backend required | JavaScript required | Static-host safe | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| CLI | implemented local | `scripts/`, `surfaces/native/cli/` | no | no | no | Current local native-style surface, not a packaged app. |
| Web workbench | implemented local | `surfaces/web/` | yes | no | no | Local/server-rendered bootstrap surface. |
| Static public site | implemented | `/` in `public_site/` | no | no | yes | Current GitHub Pages artifact. |
| Data | implemented | `/data/` files | no | no | yes | Static JSON summaries, not a live API. |
| Lite | static_demo seed | `/lite/` | no | no | yes | Old-browser/static HTML projection. |
| Text | static_demo seed | `/text/` | no | no | yes | Plain-text/text-browser projection. |
| Files | static_demo seed | `/files/` | no | no | yes | Manifest/checksum file-tree projection, no downloads. |
| Demo | static_demo seed | `/demo/` | no | no | yes | Fixture-backed resolver examples, not live search. |
| App | deferred | `/app/` | unresolved | yes | no | Future richer browser app; no framework exists. |
| API | planned contract | `/api/v1/` | yes | no | no | Future live backend handoff, not production API. |
| Snapshots | deferred with seed example | `/snapshots/` future, `snapshots/examples/static_snapshot_v0/` repo seed | no | no | yes | Format contract and seed example exist; production signed releases and public route remain future. |
| Relay | deferred with design contract | local LAN/protocol bridge | yes | no | no | Relay Surface Design v0 records future local/LAN bridge policy; no relay runtime, FTP/SMB/WebDAV/Gopher, socket listener, private-data exposure, or write/admin route is implemented. |
| Native clients | deferred | consume `/data`, `/api`, snapshots | no by default | no | no | Future Windows/macOS/etc clients; CLI is the current local surface. |

The governed machine-readable versions of this matrix are:

- `control/inventory/publication/surface_capabilities.json`
- `control/inventory/publication/surface_route_matrix.json`
- `control/inventory/publication/client_profiles.json`
- `control/inventory/publication/page_registry.json`

## Degradation Path

Do not make one modern web app serve every old client. Use projections:

1. Modern browsers may later use `/app/` or `/web/`, but those routes are
   future/deferred.
2. Standard browsers use the current no-JS static public site.
3. Old GUI browsers use `/lite/`.
4. Text browsers, terminals, screen readers, and simple automation use
   `/text/`.
5. File-tree consumers use `/files/` and `/data/`.
6. Offline or TLS-limited clients should use future signed snapshots.
7. Very old systems may later use an operator-controlled local relay.

No old-client compatibility surface may require JavaScript, a live API, private
user state, login, arbitrary local path access, or live source probes.

## Static To Live

Static publication and live backend behavior stay separate. The static site can
describe the future `/api/v1` family only as reserved/future. It must not link
to `/api/v1` as if a live backend exists.

Live backend use later requires capability flags and the Live Backend Handoff
Contract. Live probes require the Live Probe Gateway Contract plus explicit
operator approval, abuse controls, source policy review, and disabled-by-default
source gates.

## Snapshot, Relay, And Native Readiness

Snapshots now have Signed Snapshot Format v0 as a repo-local seed contract and
example. Signed Snapshot Consumer Contract v0 defines future file-tree, text,
lite HTML, relay, native, and audit-tool consumption behavior for that format.
Production/public snapshots still require:

- deterministic manifest
- checksums
- future signature policy
- consumer contract adherence
- no executable download claims
- no private data

The seed example under `snapshots/examples/static_snapshot_v0/` is not a
production signed release, does not contain real signing keys, does not include
software binaries, is not consumed by a production consumer, and is not
published as a public `/snapshots/` route.

Relay Surface Design v0 now records the separate network/security/operator
contract, protocol-candidate inventory, security/privacy defaults, and unsigned
operator checklist for future relay work. No FTP, SMB, WebDAV, Gopher, proxy,
socket listener, or LAN protocol bridge exists now.

Native clients must wait for stable-enough public data, snapshot, action,
rights/security, and live handoff contracts. Native apps must consume governed
contracts, not engine internals.

## Non-Goals

- no new runtime behavior
- no production signed snapshots, real keys, or public `/snapshots/` route
- no snapshot reader runtime or production consumer
- no relay/protocol bridge or network listener
- no native app project
- no live `/api/v1`
- no live probes
- no external observations
- no production API guarantee
- no frontend build chain
