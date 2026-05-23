# AIDE Metadata

`.aide/` holds repo-operating metadata for Eureka. It is not product runtime
behavior and does not define source truth, resolver semantics, deployment
behavior, or public API behavior.

It is also not product truth. Generated, export-only, cache, and report material
under `.aide/` is governed by `control/policies/aide_ledger_size_policy.json`.
Export-only packs are portable artifacts, not active source. Reports and
generated inventories are retention-capped evidence, not runtime authority.

Current areas:

- `commands/`: local dev and CI command metadata
- `tasks/`: JSON-subset YAML task queue and audit backlog
- `reports/`: retention-capped repo-operating report notes
- `export/`: export-only portable packages, not active source
- `generated/`, `context/`, `repo/`, `roots/`, `tools/`: generated control-plane
  material, not product truth

Use these files as coordination hints for humans, AIDE-style operators, and
Codex tasks. The current verification lane source is documented in
`control/inventory/tests/` and `docs/operations/TEST_AND_EVAL_LANES.md`.
