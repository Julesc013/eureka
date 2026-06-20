# Eureka AIDE Decisions

- Keep `EUREKA-REAL-LIVE-SEARCH-HUNT-00` as one umbrella product task until the live Search/Hunt acceptance gate passes.
- Treat `SearchLead` as transient provider output. It may be displayed immediately, but provider URLs, snippets, ranks, raw responses, and credentials must not be written to durable Hunt summaries or indexes under restrictive provider terms.
- Treat `SourceObservation` as the durable unit for independently fetched, policy-approved page content and metadata.
- Keep `PreviewDocument` and Preview Index records unreviewed but immediately useful; review gates only canonical `ReviewedRecord` creation and reviewed/public index mutation.
- Use `runtime/search/live_service.py` as the shared provider invocation and transient lead orchestration layer for CLI, HTTP, Workbench, and later clients.
- Keep public fanout and public exposure disabled while allowing bounded local `--live` provider calls under explicit operator opt-in.
- Preserve immutable Preview Index generation/export mechanics for audit, replay, rollback, and distribution; add SQLite/FTS later for operational interactive search and persistence.
- Do not start second provider families, agentic planners, public launch, renderer expansion, native/mobile work, or broad AIDE cleanup until the live local product path works.
