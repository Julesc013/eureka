# Snapshot, Relay, and Compatibility Status

Compatibility surfaces:

- Validator passed.
- Surface count: 27
- Route surface count: 13
- Implemented static surfaces: data, demo, files, lite, public_static_site, text
- Future/disabled surfaces: api, app, live_backend, live_probe_gateway, native_client, relay, snapshots

Static snapshot:

- Seed root: `snapshots/examples/static_snapshot_v0/`
- Generator check passed.
- Validator passed.
- Files: 12
- Checksum entries: 11
- Contains real binaries: false
- Production signed release: false
- Real signing keys present: false

Snapshot consumer:

- Contract/profile validator passed.
- Profiles: 6
- Production consumer implemented: false
- Native consumer implemented: false
- Relay consumer implemented: false

Relay:

- Relay surface design validator passed.
- Relay prototype planning validator passed.
- Recommended first future prototype: `local_static_http_relay_prototype`
- Implementation approved: false
- Human approval required: true
- Relay runtime files: 0
- No sockets, protocol servers, private file serving, live proxying, or write/admin behavior exists.
