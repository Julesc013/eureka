# Eureka AIDE Open Risks

- The live product path is still incomplete: safe fetch, extraction, durable SQLite/FTS Preview Indexing, restart retrieval proof, and real budgeted Hunt remain pending.
- Local `--live` provider calls depend on an operator-provided key and must keep credentials out of Git, chat, logs, summaries, and client-side code.
- Brave Search Results are provider outputs with restrictive retention terms; accidental persistence of URLs, snippets, ranks, or raw responses would violate the current design boundary and requires focused tests.
- Public live fanout remains disabled. Local `--live` canaries must not be interpreted as public launch, tunnel/exposure readiness, or production readiness.
- Current Hunt is still deterministic query expansion and provider search only. It does not fetch, inspect, index, pause/resume/cancel, or persist SourceObservations.
- The operational Preview Index is still not scaled for large incremental search; SQLite/FTS is required before serious local corpus growth.
- Documentation and AIDE state should stay subordinate to runtime truth. Avoid duplicating volatile current-state claims beyond README, STATUS, ROADMAP, and the current task packet.
- Future agents must not request human acceptance until an unseen query proves live results, Hunt expansion, independent fetch, durable local indexing, restart retrieval, honest provider failure, no fixture substitution, no review obstruction, no provider-result persistence, and no reviewed/public mutation.
