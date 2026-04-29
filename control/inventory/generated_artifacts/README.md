# Generated Artifact Inventory

Generated Artifact Drift Guard v0 records repo-local generated and
generated-like artifacts that are committed on purpose. The inventory keeps
ownership explicit so public data, static surfaces, snapshot examples, Python
oracle goldens, public-alpha rehearsal evidence, publication inventories, test
registry metadata, and AIDE metadata can be checked without changing product
runtime behavior.

The guard is validation-only. It delegates to existing generator `--check`
commands, validators, and governance tests. It does not run update commands,
regenerate committed outputs, call external services, open network sockets,
deploy, or claim production readiness.

Files:

- `generated_artifacts.json` lists artifact groups, source inputs, owning
  check commands, validators, volatility notes, and committed-output policy.
- `drift_policy.json` defines drift classes, allowed skips, unavailable-tool
  handling, Cargo handling, and the no-network rule.

