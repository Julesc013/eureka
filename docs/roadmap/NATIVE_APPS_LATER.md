# Native Apps Later

Native app work is intentionally deferred until backend contracts and the hosted
alpha path are stronger.

## Current Policy

- no Visual Studio project yet
- no Xcode project yet
- no full native app work yet

Thin host shells may be explored later as experiments, but they should remain
downstream of stronger backend and public-boundary work.

Source Registry v0 does not change that policy by itself. Backend infrastructure
still takes priority over host shells.

Rust Migration Skeleton and Parity Plan v0 does not change that policy. The
Rust skeleton does not change that policy either: the workspace is a backend
parity lane only; it is not a native app project, does not add FFI, and does
not start host-shell work.

Rust Parity Fixture Pack v0 also does not change that policy. The Python-oracle
golden outputs are migration evidence for future backend seams; they are not a
native SDK, app shell, FFI layer, or runtime replacement.

Rust Source Registry Parity Candidate v0 does not change that policy either. It
is a crate-local source-registry parity seam, not a native SDK, FFI layer, app
shell, or runtime replacement.

Compatibility Surface Strategy v0 also keeps that policy. It records native
client readiness rules and surface capability matrices, but it does not create
a Windows/macOS project, native SDK, installer, FFI layer, sync client, or app
shell. The CLI remains the current local native-style surface.

Signed Snapshot Format v0 also keeps that policy. It defines a static/offline
snapshot contract and deterministic seed example for future clients, but it
does not create production signed releases, real signing keys, executable
downloads, a native SDK, app shell, sync client, relay runtime, or any native
project.

Signed Snapshot Consumer Contract v0 also keeps that policy. It defines how
future file-tree, text, lite HTML, relay, native, and audit consumers should
read snapshot manifests, validate checksums, and treat v0 signatures as
placeholders, but it does not implement a native consumer, SDK, sidecar,
installer, app shell, production signing, real keys, executable downloads, or
relay runtime.

Relay Surface Design v0 also keeps that policy. It defines future local/LAN
relay architecture, security/privacy defaults, protocol candidates, and an
operator checklist, but it does not create a native sidecar, app shell, SDK,
network service, protocol bridge, private-data path, write/admin route, or live
probe passthrough.

## Host-Shell Principle

Future native apps should remain shells over the core. They should consume
public or SDK boundaries rather than re-implement resolver truth locally.

## Design Direction

When native work begins, the interaction model may be informed by:

- Mac App Store-style catalog and detail affordances
- Windows Marketplace or pre-Windows-Store distribution patterns

That design inspiration should not change the architectural rule that apps are
hosts over the resolver core rather than separate resolver implementations.

## Earliest Sensible Start

Serious native host work should wait until:

- source registry and planner shapes are clearer
- resolution runs exist
- local index work is underway
- public-alpha-safe boundaries are clearer
- public data contracts and static export contracts are stable enough
- signed/offline snapshot format exists
- snapshot consumer read order, checksum, and signature-placeholder contract
  exists
- relay security/privacy and operator policy exists, with runtime still
  explicitly deferred
- rights, security, download, and action-handoff policies exist
- Rust parity boundaries are clearer if native shells later consume Rust
  libraries directly

## Native/Relay Checkpoint

Post-Queue State Checkpoint v0 records the current post-queue evidence and
verification state under `control/audits/post-queue-state-checkpoint-v0/`. It
is audit/reporting only; it does not add backend hosting, live probes,
production deployment, Rust runtime wiring, relay services, or native app
projects.
