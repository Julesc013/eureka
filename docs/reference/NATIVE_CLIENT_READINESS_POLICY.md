# Native Client Readiness Policy

Native app projects remain deferred. The current local native-style surface is
the CLI/local scripts path, not a packaged Windows or macOS app.

Prerequisites before native GUI client work starts:

- stable-enough public data contracts
- static export and snapshot format contracts; Signed Snapshot Format v0 is a
  seed example and contract only, not a native-client release format guarantee
- Signed Snapshot Consumer Contract v0 for read order, checksum validation,
  v0 signature-placeholder handling, and missing optional file behavior
- live backend handoff contract for optional online mode
- source, evidence, result-lane, action, and absence models stable enough for
  client consumption
- rights/security/download policy before any fetch/install workflow
- clear local-cache and offline snapshot semantics
- relay security/privacy and operator policy for any sidecar or LAN bridge
- Native Client Contract v0 lane and readiness checklist reviewed
- Native Action / Download / Install Policy v0 before any download, install,
  open, restore, or package-manager handoff behavior
- Native Local Cache / Privacy Policy v0 before any native cache runtime,
  private cache, private ingestion, telemetry, diagnostics upload, accounts,
  cloud sync, or local archive scanning behavior
- Native Client Project Readiness Review v0 before any Visual Studio, Xcode,
  GUI, FFI, cache runtime, download, installer, relay, live-probe, or native
  project scaffolding work
- executable-risk and rights/access labels before any future risky handoff
- no dependency on private engine internals

Installer automation remains deferred until rights, security, executable-risk,
hash/checksum, and action-handoff policies exist.
Native Action / Download / Install Policy v0 now seeds those gates as policy
only: no downloads, installers, package-manager integration, malware scanning,
rights clearance, or executable trust claims are implemented.

Native Local Cache / Privacy Policy v0 now seeds local cache, private data,
local path, telemetry/logging, credential, deletion/export/reset, portable
mode, snapshot, relay, and public-alpha privacy gates as policy only. It adds
no cache runtime, private file ingestion, local archive scanning, telemetry,
accounts, cloud sync, uploads, native clients, or relay runtime.

Native Client Project Readiness Review v0 now records the first readiness
decision: `ready_for_minimal_project_skeleton_after_human_approval` for
`windows_7_x64_winforms_net48` only. This is review/evidence only and does not
create native project files, app source trees, GUI behavior, FFI, cache runtime,
downloads, installers, relay runtime, live probes, or runtime wiring.

Future Windows and macOS lane docs may define prototypes later, but they must
consume governed public data, future production snapshots, or live handoff
contracts. They must not become a back door into runtime internals. The current
snapshot seed includes no real signing keys, no production signatures, no
executable downloads, no relay service, and no native-client runtime. Relay
Surface Design v0 records sidecar/LAN bridge policy only and does not add a
native sidecar or protocol implementation.

Signed Snapshot Consumer Contract v0 does not implement a native consumer. It
defines the future snapshot consumption contract that Native Client Contract v0
can reference without starting Visual Studio, Xcode, installer, sidecar, or
packaged runtime work.

Native Client Contract v0 is now implemented as contract/design only. It
records future Windows and Mac lanes, CLI current-state boundaries, allowed
inputs, prohibited actions, and verification checks, but it does not create
native GUI clients, Visual Studio or Xcode projects, FFI, native snapshot
reader runtimes, relay sidecars, installer automation, package-manager
behavior, download/execution automation, live probes, or Rust runtime wiring.
