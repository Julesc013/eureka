# Eureka Node Manifest Contract

The Eureka Node manifest is a contract-only identity record for future worker identities. A node may later prepare local candidates, source leads, evidence drafts, contribution pack drafts, review items, and WorkUnit results.

A node is not a runtime in this milestone. It does not run WorkUnits, create local state, call networks, call models or providers, perform observations, download files, upload packs, create accounts, emit telemetry, or mutate the master index.

## Modes

- `local_private`: local/private candidate state only; no submission or public mutation.
- `local_pack_builder`: pack validation and future pack drafting/export; no automatic upload or acceptance.
- `local_autonomous_dry_run`: local planning and simulation only; no live source access or mutation.
- `community_node_future`: future public-need worker, review-gated and inactive.
- `institution_node_future`: future institutional collection/source namespace worker, review-gated and inactive.
- `hosted_worker_future`: future official governed worker, inactive in this milestone.

## Truth Boundary

Node output can become a local candidate, source lead, evidence draft, contribution pack draft, review item, or future WorkUnit result. It cannot become accepted public truth, accepted evidence truth, master-index mutation, rights clearance, malware safety, verified installability, or exhaustive search proof without later explicit review and promotion.

## Required Boundaries

Every current manifest must keep network access disabled, forbid unapproved source access, forbid master-index mutation, require review for public export and evidence acceptance, and keep pack import/upload/hosted submission disabled.

Validation:

```powershell
python scripts/validate_eureka_node_manifest.py
```
