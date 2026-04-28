# Compatibility Surface Status

Implemented or seeded surfaces include local CLI, local web workbench, local HTTP/API prototype lanes, the static public site, generated public data, lite HTML, text, files, and static demo snapshots.

Seeded-only static compatibility surfaces are `lite/`, `text/`, and `files/`. Future/deferred surfaces include `/app/`, `/api/v1`, `/snapshots/`, relay, and native clients.

Compatibility strategy is documented in `docs/architecture/COMPATIBILITY_SURFACES.md`. The rule remains: same resolver truth, multiple projections; do not make one modern app pretend to serve every old client.
