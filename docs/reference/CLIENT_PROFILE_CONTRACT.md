# Client Profile Contract

Client profiles are registered in
`control/inventory/publication/client_profiles.json`.

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
- `api_client`: future public data and API consumer profile; not a live backend
  guarantee.

Profiles describe consumption contracts. Lite/Text/Files Seed Surfaces v0 now
implements seed static surfaces for `lite_html`, `text`, and `file_tree`.
Static Resolver Demo Snapshots v0 adds static `/demo/` examples for
`standard_web` and `lite_html` consumption, but it does not add interactive app,
snapshot, relay, native-client, or live API behavior. Profiles still do not
implement `/app/`, snapshots, relay behavior, native clients, or live APIs by
themselves.
