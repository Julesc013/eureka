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
- `local_staging_manifest_format` references are recorded in the staging model
  and path contract. The governed schema lives at
  `contracts/packs/local_staging_manifest.v0.json`, with a synthetic example
  under `examples/local_staging_manifests/`.
- Staged Pack Inspector v0 is recorded in the staging model and path contract.
  `scripts/inspect_staged_pack.py` is read-only and stdout-only: it inspects
  explicit manifests, explicit roots, or committed synthetic examples and does
  not create staging runtime, staged state, import behavior, local index
  mutation, public-search mutation, upload, or master-index mutation.

Future local staging remains disabled by default. No `.eureka-local/`,
`.eureka-cache/`, `.eureka-staging/`, or `.eureka-reports/` directory should
be committed.
