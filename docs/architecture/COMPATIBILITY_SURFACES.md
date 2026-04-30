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
service, native client, native GUI project, FFI, installer automation, live
`/api/v1`, or live probe is implemented.

Compatibility Surface Strategy v0 does not implement new runtime product behavior.

## Surface Families

| Surface | Current status | Root or consumer | Backend required | JavaScript required | Static-host safe | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| CLI | implemented local | `scripts/`, `surfaces/native/cli/` | no | no | no | Current local native-style surface, not a packaged app. |
| Web workbench | implemented local | `surfaces/web/` | yes | no | no | Local/server-rendered bootstrap surface. |
| Static public site | implemented | `/` in `site/dist/` | no | no | yes | Current GitHub Pages artifact. |
| Data | implemented | `/data/` files | no | no | yes | Static JSON summaries, not a live API. |
| Lite | static_demo seed | `/lite/` | no | no | yes | Old-browser/static HTML projection. |
| Text | static_demo seed | `/text/` | no | no | yes | Plain-text/text-browser projection. |
| Files | static_demo seed | `/files/` | no | no | yes | Manifest/checksum file-tree projection, no downloads. |
| Demo | static_demo seed | `/demo/` | no | no | yes | Fixture-backed resolver examples, not live search. |
| App | deferred | `/app/` | unresolved | yes | no | Future richer browser app; no framework exists. |
| API | planned contract | `/api/v1/` | yes | no | no | Future live backend handoff, not production API. |
| Public search API | local prototype runtime | `/search`, `/api/v1/search` | yes | no | no | Public Search API Contract v0 plus Local Public Search Runtime v0 expose local-index-only search through the stdlib backend; hosted deployment and static handoff remain future. |
| Snapshots | deferred with seed example | `/snapshots/` future, `snapshots/examples/static_snapshot_v0/` repo seed | no | no | yes | Format contract and seed example exist; production signed releases and public route remain future. |
| Relay | deferred with design contract | local LAN/protocol bridge | yes | no | no | Relay Surface Design v0 records future local/LAN bridge policy; no relay runtime, FTP/SMB/WebDAV/Gopher, socket listener, private-data exposure, or write/admin route is implemented. |
| Native clients | deferred with design contract | consume `/data`, `/api`, snapshots | no by default | no | no | Native Client Contract v0 records future Windows/macOS lanes; CLI is the current local surface. |

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

Public Search API Contract v0 sits between those two layers: it defines
request, response, error, and route envelopes for `local_index_only` search.
Local Public Search Runtime v0 implements `/search`, `/api/v1/search`,
`/api/v1/query-plan`, `/api/v1/status`, `/api/v1/sources`, and
`/api/v1/source/{source_id}` as local/prototype backend routes only. It does
not add hosted deployment, live probes, arbitrary URL fetching, downloads,
installs, uploads, local path search, accounts, telemetry, or production API
stability. Public Search Static Handoff v0 now adds static/no-JS standard,
lite, text, files, and data handoff outputs without making hosted search live.
Public Search Result Card Contract v0 refines the future `results[]` unit that
those envelopes will carry. It keeps lane, user-cost, source, evidence,
compatibility, action gating, rights, risk, warnings, limitations, and gaps
visible to web/API/lite/text/native/relay/snapshot consumers without adding
runtime search, downloads, installers, execution, uploads, live probes, malware
safety, rights clearance, or production ranking guarantees.

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

Relay Prototype Planning v0 now records the first future prototype choice:
local static HTTP, localhost-only by default, read-only, and limited to
allowlisted public data plus seed snapshot files. It is planning only and adds
no relay runtime, socket listener, local HTTP relay, protocol server, private
file serving, live backend proxy, live probe path, native sidecar, or old-client
relay support claim.

Native Client Contract v0 now records future Windows/macOS/native lanes,
allowed inputs, CLI current-state boundaries, and readiness gates. Native
clients must wait for stable-enough public data, snapshot, action,
rights/security, and live handoff contracts. Native apps must consume governed
contracts, not engine internals, and no Visual Studio/Xcode project, native
GUI, FFI, installer automation, relay sidecar, or Rust runtime wiring exists.
Native Action / Download / Install Policy v0 now records the future action,
download, install handoff, package-manager handoff, mirror, execute,
rights/access, and executable-risk policy those clients must obey. It is
policy-only and adds no downloads, installers, package-manager integration,
malware scanning, rights clearance, native client runtime, or relay runtime.

Native Local Cache / Privacy Policy v0 now records the future cache/privacy,
private-data, local-path, telemetry/logging, credential, deletion/export/reset,
portable-mode, snapshot, relay, and public-alpha policy those clients must
obey. It is policy-only and adds no cache runtime, private file ingestion,
local archive scanning, telemetry, accounts, cloud sync, uploads, native client
runtime, private-data relay behavior, or relay runtime.

## Non-Goals

- no new runtime behavior
- no production signed snapshots, real keys, or public `/snapshots/` route
- no snapshot reader runtime or production consumer
- no relay/protocol bridge or network listener
- no native app project
- no native GUI, FFI, installer automation, or executable download automation
- no native cache runtime, private ingestion, telemetry, accounts, cloud sync,
  uploads, or local archive scanning
- no malware safety claim, rights clearance claim, package-manager integration,
  mirror behavior, or install handoff implementation
- no live `/api/v1`
- no live probes
- no external observations
- no production API guarantee
- no frontend build chain
