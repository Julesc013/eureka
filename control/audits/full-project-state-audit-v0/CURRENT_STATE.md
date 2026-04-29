# Current State

Eureka remains a monorepo bootstrap/pre-product system. Python is the active oracle and runtime reference. Rust is present only as isolated parity candidate/planning material. AIDE remains repository operating metadata only.

Current implemented or seed surfaces:

- Python source registry, planner, local index, ranking/lane/user-cost, compatibility evidence, memory/run/task seams, and bounded acquisition fixtures.
- Public-alpha local wrapper with safe-mode config; not deployed here.
- `public_site/` as the current static artifact.
- `site/` generator and `site/dist/` generated output, with `public_site/` still the deployment artifact.
- `public_site/data/`, `public_site/lite/`, `public_site/text/`, `public_site/files/`, and `public_site/demo/`.
- Static snapshot seed under `snapshots/examples/static_snapshot_v0/`.
- CLI under `surfaces/native/cli/` as the only implemented native-like surface.

Current contract/planning surfaces:

- Publication plane, GitHub Pages static artifact, static host/domain readiness, live backend handoff, live probe gateway, compatibility surfaces, signed snapshot format/consumer, relay design/prototype plan, native client contract/policies, native readiness review, and Windows 7 WinForms skeleton planning.

Not currently implemented:

- Relay runtime, network sockets, protocol servers, live backend, live probes, native GUI apps, Visual Studio/Xcode projects, local cache runtime, private ingestion, telemetry, accounts, cloud sync, downloads, installers, malware scanning, rights clearance, production signing, real signing keys, and production deployment approval.
