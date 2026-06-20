# Eureka AIDE Open Risks

- The deterministic live product path is implemented, but real live acceptance is still unproven until `OPERATOR-LIVE-CANARY-00` runs with a local Brave key and proves live result, Hunt, independent fetch, SourceObservation, PreviewDocument, restart retrieval, no provider payload persistence, and no reviewed/public mutation.
- Local `--live` provider calls depend on an operator-provided key and must keep credentials out of Git, chat, logs, summaries, and client-side code.
- Brave Search Results are provider outputs with restrictive retention terms; accidental persistence of URLs, snippets, ranks, or raw responses would violate the current design boundary and requires focused tests.
- Public live fanout remains disabled. Local `--live` canaries must not be interpreted as public launch, tunnel/exposure readiness, or production readiness.
- Second provider and Foundry are implemented but intentionally gated: IA metadata is unreviewed metadata, and Foundry is disabled by default with explicit local operator activation only.
- Operational recovery, backup, migration, diagnostics, performance baseline, provider policy registry validation, portable release rehearsal, and hardening audit remain Wave 03 work.
- Documentation and AIDE state should stay subordinate to runtime truth. Avoid duplicating volatile current-state claims beyond README, STATUS, ROADMAP, and the current task packet.
- Future agents must not request human acceptance until the real live canary proves live results, Hunt expansion, independent fetch, durable local indexing, restart retrieval, honest provider failure, no fixture substitution, no review obstruction, no provider-result persistence, and no reviewed/public mutation.
