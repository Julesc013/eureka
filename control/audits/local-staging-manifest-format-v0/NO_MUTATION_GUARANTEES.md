# No-Mutation Guarantees

Every Local Staging Manifest v0 must record:

- `public_search_mutated: false`
- `local_index_mutated: false`
- `canonical_source_registry_mutated: false`
- `runtime_state_mutated: false`
- `master_index_mutated: false`
- `upload_performed: false`
- `live_network_performed: false`

The same values appear inside `no_mutation_guarantees`. The validator rejects
manifests that claim mutation, upload, network access, or master-index impact.

Manifest validation is not staging runtime, not import, not local index
mutation, not public search mutation, and not master-index acceptance.
