# AIDE Metadata

`.aide/` holds repo-operating metadata for Eureka. It is not product runtime
behavior and does not define source truth, resolver semantics, deployment
behavior, public API behavior, or accepted product semantics.

It is not product truth. Generated, export-only, cache, and report material
under `.aide/` is governed by retention-capped policy. Export-only packs are
portable artifacts, not active source. Reports and generated inventories are
repo-operating evidence, not runtime authority.

Current areas:

- `commands/`: local dev and CI command metadata.
- `queue/` and `tasks/`: task queue and task metadata.
- `reports/`: repo-operating report notes.
- `context/`: compact task/review packets.
- `export/`: export-only portable packages.
- `generated/`, `repo/`, `roots/`, `tools/`: generated control-plane material.

Use these files as coordination hints for humans, AIDE-style operators, and
Codex tasks. Product truth lives in `contracts/`, `runtime/`, reviewed records,
and accepted architecture docs.
