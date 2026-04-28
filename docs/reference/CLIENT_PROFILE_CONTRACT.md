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
- `lite_html`: future old-browser HTML surface.
- `text`: future text-browser and terminal-readable surface.
- `file_tree`: future static file, manifest, and checksum tree.
- `snapshot`: future offline static bundle profile.
- `native_client`: future native clients consuming public data, API, or
  snapshots.
- `relay`: future local LAN or legacy protocol bridge.
- `api_client`: future public data and API consumer profile; not a live backend
  guarantee.

Profiles describe consumption contracts. They do not implement `/app/`, `/lite/`,
`/text/`, `/files/`, snapshots, relay behavior, native clients, or live APIs by
themselves.

