# Local State Inventory

This inventory records future local/private state policy for Eureka. It is
repo-operating governance only and does not create a staging runtime, local
cache, local index mutation path, public-search mutation path, or master-index
submission path.

Current files:

- `local_quarantine_staging_model.json`: planning-only model for future local
  quarantine/staging after validate-only pack reports.
- `local_state_path_policy.json`: future path policy and prohibited roots for
  private/local state.
- `staging_report_path_contract.json`: planning-only contract for stdout
  defaults, explicit output paths, safe local report roots, forbidden committed
  roots, filename safety, and redaction.

Future local staging remains disabled by default. No `.eureka-local/`,
`.eureka-cache/`, `.eureka-staging/`, or `.eureka-reports/` directory should
be committed.
