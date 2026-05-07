# Documentation Quality Standard

Eureka docs should be accurate, source-grounded, compact, and explicit about
status, no-goals, validation, deferred work, and product-boundary claims.

## Anti-Bloat Rules

- Do not paste full chat history.
- Do not repeat large project-history blocks in every audit.
- Link to canonical docs instead of copying them.
- Summarize task-local changes.
- Preserve exact no-goals when risk-bearing.
- Do not claim production, hosted, or live-source behavior without evidence.

## Stale-Claim Checks

Docs should avoid unsupported claims about hosted backends, live probes, source
sync, source connectors, downloads/installers/execution, uploads/accounts/
telemetry, rights clearance, malware safety, verified installability,
exhaustive global search, automatic merge/dedup/promotion, master-index
mutation, or native project creation.

## Surface Guidance

Use `docs/reference` for governed contracts, `docs/architecture` for accepted
architecture, `docs/operations` for commands and expected validation,
`docs/roadmap` for sequencing, and `control/audits` for task-local evidence.

The machine-readable source of truth is
`.aide/policies/documentation-quality-policy.yaml`.
