# AIDE Metadata

`.aide/` holds repo-operating metadata for Eureka. It is not product runtime
behavior and does not define source truth, resolver semantics, deployment
behavior, or public API behavior.

Current areas:

- `commands/`: local dev and CI command metadata
- `tasks/`: JSON-subset YAML task queue and audit backlog
- `reports/`: reserved repo-operating report notes

Use these files as coordination hints for humans, AIDE-style operators, and
Codex tasks. The current verification lane source is documented in
`control/inventory/tests/` and `docs/operations/TEST_AND_EVAL_LANES.md`.

