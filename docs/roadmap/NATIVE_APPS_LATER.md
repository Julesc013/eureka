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

Relay Prototype Planning v0 also keeps that policy. It chooses a future
localhost-only/read-only/static local HTTP relay prototype shape for public
data and seed snapshots, but it does not create a relay runtime, socket,
native sidecar, snapshot mount, private file server, live backend proxy, live
probe path, or old-client relay support.

Native Client Contract v0 also keeps that policy. It defines future Windows and
Mac client lanes, CLI current-state boundaries, snapshot/public-data/live
handoff/relay/Rust dependencies, and readiness gates, but it does not create a
Visual Studio project, Xcode project, native GUI, FFI layer, native snapshot
reader runtime, relay sidecar, installer automation, package-manager behavior,
download/execution automation, live probes, or Rust runtime wiring.

Native Action / Download / Install Policy v0 also keeps that policy. It defines
future inspect, preview, export, download, mirror, install handoff,
package-manager handoff, execute, restore, uninstall, rollback, malware-scan,
and rights/access gates, but it does not implement downloads, installers,
package-manager integration, malware scanning, rights clearance, executable
trust claims, native clients, relay runtime, or any public download surface.

Native Local Cache / Privacy Policy v0 also keeps that policy. It defines
future public/private cache, local path, user state, telemetry/logging,
diagnostics, credentials, deletion/export/reset, portable mode, snapshot,
relay, and public-alpha privacy gates, but it does not implement cache runtime,
private file ingestion, local archive scanning, telemetry, analytics, accounts,
cloud sync, uploads, native clients, relay runtime, or any private-data relay
surface.

Native Client Project Readiness Review v0 records the first evidence-based
native project decision. The repo is ready for a minimal
`windows_7_x64_winforms_net48` skeleton only after explicit human approval, and
only as read-only public data / seed snapshot inspection planning. It does not
create a Visual Studio project, Xcode project, native app source tree, GUI
behavior, FFI, local cache runtime, downloads, installers, relay runtime, live
probes, or runtime wiring.

Windows 7 WinForms Native Skeleton Planning v0 records the first future
Windows skeleton plan. It proposes `clients/windows/winforms-net48/` and
`Eureka.Clients.Windows.WinForms`, documents Windows host, Visual Studio 2022,
.NET Framework 4.8, x64, Windows 7 SP1+ requirements, and limits any future
skeleton to read-only static public data and seed snapshot demo inspection. It
does not create `clients/`, a Visual Studio solution, `.csproj`, C# source,
GUI behavior, FFI, local cache runtime, downloads, installers, telemetry,
relay runtime, live probes, or runtime wiring. Any implementation still
requires explicit human approval.

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
- native client lane, dependency, and readiness contract exists
- Native Action / Download / Install Policy v0 exists before any download,
  install, open, restore, or package-manager handoff behavior
- local cache, retention, and privacy policy exists before native project work
- native project readiness review records a human-approval gate and first-lane
  decision before any Visual Studio or Xcode scaffold
- Windows 7 WinForms Native Skeleton Planning v0 is reviewed and its proposed
  path, namespace, read-only scope, build-host requirements, and approval gate
  are explicitly accepted before any skeleton implementation
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

Full Project State Audit v0 records the current native and relay state after
the Windows 7 WinForms skeleton plan and Relay Prototype Planning v0. The
Windows skeleton and relay prototype are both ready only as human-approved
future implementation candidates; no Visual Studio/Xcode project, GUI, relay
runtime, socket, cache runtime, download/install behavior, telemetry, or live
probe was added.
