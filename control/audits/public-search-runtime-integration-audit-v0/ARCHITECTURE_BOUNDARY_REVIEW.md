# Architecture Boundary Review

Expected boundary:

- Public search should read controlled public/local index records and governed
  source registry summaries only.
- Source-cache and evidence-ledger dry-run runtimes should remain CLI/local and
  non-authoritative.
- Planning packs should not become runtime behavior.
- Connector runtimes should remain disabled, planning-only, or approval-gated
  until explicitly approved.
- Page, ranking, explanation, deep extraction, and pack import work should not be
  public-search integrated yet.

Audit result:

- No unexpected integration was found.
- `runtime/source_cache` and `runtime/evidence_ledger` are local dry-run packages,
  not gateway dependencies.
- Public search gateway code remains in `runtime/gateway/public_api/` and does not
  import the P98/P99 dry-run runtimes.
- Architecture-boundary validation is required after this audit.

Stale claim risk:

- Hosted wrapper and static handoff docs must continue to say local/prototype or
  backend-unconfigured until real hosted evidence exists.

