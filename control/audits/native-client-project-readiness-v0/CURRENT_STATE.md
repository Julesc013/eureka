# Current State

Eureka remains a bootstrap and pre-product repository. Python is the active
reference/oracle lane. Rust remains isolated parity and planning work. The CLI
under `surfaces/native/cli/` is the only current native-like local surface.

Current facts:

- No GUI native app is implemented.
- No Visual Studio project is present.
- No Xcode project is present.
- No native app source tree is present.
- No FFI boundary is implemented.
- No native snapshot reader runtime is implemented.
- No local cache runtime is implemented.
- No private file ingestion or local archive scanning is implemented.
- No telemetry, analytics, accounts, cloud sync, or diagnostic upload is implemented.
- No download, installer, package-manager, execute, restore, uninstall, or rollback automation is implemented.
- No relay runtime or old-client protocol server is implemented.
- Public-alpha remains non-production and local/safe-mode only.
- GitHub Pages remains static-only through `public_site/`.

Contracts and evidence now present:

- Native Client Contract v0
- Native Client Lanes inventory
- Native Action / Download / Install Policy v0
- Native Local Cache / Privacy Policy v0
- Signed Snapshot Consumer Contract v0
- Signed Snapshot Format v0 seed example
- Relay Surface Design v0
- Compatibility Surface Strategy v0
- Public Publication Plane contracts and generated public data
- Lite/Text/Files static seed surfaces
- Static resolver demo snapshots
- Live Backend Handoff Contract v0, contract-only and disabled
- Live Probe Gateway Contract v0, contract-only and disabled
- Rust source-registry/query-planner candidates and local-index parity plan, all unwired

The current native posture is therefore: contract coverage is good enough to
start a human-reviewed minimal skeleton planning lane, but not enough to start
a native prototype with behavior beyond read-only public metadata and static
snapshot inspection.

