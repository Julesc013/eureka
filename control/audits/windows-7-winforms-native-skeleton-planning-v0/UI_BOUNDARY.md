# UI Boundary

The future skeleton UI may be a small read-only status shell.

Initial panels may include:

- title and non-production banner
- static data load status
- source summary
- eval summary
- demo query list
- limitations
- evidence/provenance placeholder panel

The UI must not include:

- download buttons
- install buttons
- open/run buttons
- package-manager handoff controls
- local cache controls
- private path picker
- account or login UI
- telemetry/analytics settings
- relay start/stop controls
- live source probe controls
- Rust backend/FFI controls

Every result or summary card must preserve source/evidence uncertainty and
must not imply executable safety, rights clearance, production readiness, or
live source availability.

