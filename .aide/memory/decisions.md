# Eureka AIDE Decisions

- Keep `EUREKA-REAL-LIVE-SEARCH-HUNT-00` as one umbrella product task until the live Search/Hunt acceptance gate passes.
- Treat `SearchLead` as transient provider output. It may be displayed immediately, but provider URLs, snippets, ranks, raw responses, and credentials must not be written to durable Hunt summaries or indexes under restrictive provider terms.
- Treat `SourceObservation` as the durable unit for independently fetched, policy-approved page content and metadata.
- Keep `PreviewDocument` and Preview Index records unreviewed but immediately useful; review gates only canonical `ReviewedRecord` creation and reviewed/public index mutation.
- Use `runtime/search/live_service.py` as the shared provider invocation and transient lead orchestration layer for CLI, HTTP, Workbench, and later clients.
- Use `runtime/search/discovery_broker.py` above provider invocation for deterministic intent classification, local-first planning, provider health/status checks, bounded fanout, lead fusion, and cost/yield accounting.
- Keep public fanout and public exposure disabled while allowing bounded local `--live` provider calls under explicit operator opt-in.
- Preserve immutable Preview Index generation/export mechanics for audit, replay, rollback, and distribution; SQLite/FTS is now the operational local Preview Index for unreviewed SourceObservations.
- Treat Internet Archive metadata as a vertical provider, not a broad-web acceptance substitute; the live canary still requires at least one healthy approved broad-web provider.
- Treat Foundry v0 as implemented, local, and disabled by default. It may grow only the unreviewed Preview Index through explicit operator commands and may not create reviewed truth.
- Do not start agentic planners, public launch, renderer expansion, native/mobile work, or broad AIDE cleanup until the live canary, human acceptance, external full discovery, and hardening audit gates pass.
