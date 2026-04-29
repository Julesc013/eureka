# Drift Policy

Generated Artifact Drift Guard v0 uses the policy in
`control/inventory/generated_artifacts/drift_policy.json`.

Drift classes:

- `missing_artifact`: a required committed generated artifact path is absent.
- `stale_generated_output`: an owning check command reports stale output.
- `generator_missing`: a declared Python generator script cannot be found.
- `check_command_missing`: a required check command cannot be resolved.
- `volatile_field_uncontrolled`: a known volatile field lacks normalization or
  policy coverage.
- `untracked_generated_output`: generated output appears without an inventory
  owner.
- `orphan_generated_output`: generated-like output has no owner or check.

Default mode is deterministic and non-mutating. It does not run update commands
and does not mutate artifacts.

Cargo is optional. Cargo absence is not a drift failure for this milestone.

Network behavior is prohibited. Drift checks must not call external APIs, fetch
URLs, scrape, crawl, run live probes, deploy, or open persistent services.

