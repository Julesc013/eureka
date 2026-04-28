# Client Profile Contract

Client profiles are registered in
`control/inventory/publication/client_profiles.json`.

Compatibility Surface Strategy v0 aligns these profiles with
`control/inventory/publication/surface_capabilities.json` and
`control/inventory/publication/surface_route_matrix.json`. Profiles describe
which clients may consume a surface; they do not implement the surface by
themselves.

Every profile must define:

- `id`
- `status`
- `intended_clients`
- `requires_javascript`
- `requires_css`
- `requires_https`
- `intended_path_prefixes`
- `must_support`
- `prohibited_dependencies`
- `current_support_level`
- `notes`

Required profiles:

- `modern_web`: future richer browser experience; not active as an app surface.
- `standard_web`: current no-JS static public pages where applicable.
- `lite_html`: static_demo old-browser HTML seed surface under `/lite/`.
- `text`: static_demo text-browser and terminal-readable seed surface under
  `/text/`.
- `file_tree`: static_demo static file, manifest, and checksum seed tree under
  `/files/`.
- `snapshot`: future offline static bundle profile.
- `native_client`: future native clients consuming public data, API, or
  snapshots.
- `relay`: future local LAN or legacy protocol bridge.
- `api_client`: current static public data consumer and future `/api/v1`
  handoff consumer profile; not a live backend guarantee.

Profiles describe consumption contracts. Lite/Text/Files Seed Surfaces v0 now
implements seed static surfaces for `lite_html`, `text`, and `file_tree`.
Static Resolver Demo Snapshots v0 adds static `/demo/` examples for
`standard_web` and `lite_html` consumption, but it does not add interactive app,
snapshot, relay, native-client, or live API behavior. Profiles still do not
implement `/app/`, snapshots, relay behavior, native clients, or live APIs by
themselves.

Signed Snapshot Consumer Contract v0 updates the `snapshot` profile
expectation: future consumers must read the required snapshot files in the
governed order, validate checksums where possible, and treat v0 signatures as
placeholders. This does not implement a snapshot consumer, relay, native
client, production signing, real signing keys, executable downloads, live
backend behavior, or live probes.

Live Backend Handoff Contract v0 updates the `api_client` expectation: clients
may know that `/api/v1` is reserved, but they must treat it as future and
disabled unless a status/capability document says `live_backend` is enabled.

Live Probe Gateway Contract v0 adds a related caveat: static clients may read
the disabled live-probe capability summaries, but they must not assume Internet
Archive, Wayback, GitHub, package-registry, or other external source probes are
available unless a later hosted backend explicitly enables those capabilities.

Old-client degradation is explicit: do not make one modern web app serve every
old client. Use standard static pages, lite HTML, text, files, future
snapshots, and future relay projections as appropriate. Native clients remain
deferred until public data, snapshot, handoff, rights, and security policies
are stable enough for client consumption.
