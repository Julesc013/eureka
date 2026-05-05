# Remaining Blockers

- Runtime compatibility-aware ranking remains future work. P85 defines only schemas, examples, validators, docs, and audit evidence.
- Public search ordering is unchanged; no compatibility ranking, hidden suppression, installability, package-manager, emulator, VM, or execution behavior is enabled.
- Hosted deployment remains operator-gated. The hosted backend URL is not configured and configured static checks did not verify a deployed static site.
- Manual Observation Batch 0 remains pending: batch 0 has 0 observed external baseline records and 39 pending manual observations; global external-baseline slots remain 0 observed and 192 pending.
- Compatibility evidence packs and future compatibility evidence ingestion remain deferred to a later contract/runtime planning branch.
- Live source connectors remain approval-gated/deferred; no live connector, source sync, source cache, evidence ledger, candidate promotion, public-index mutation, or master-index mutation was implemented.
- Optional Rust verification was unavailable because `cargo` is not installed in this environment.
