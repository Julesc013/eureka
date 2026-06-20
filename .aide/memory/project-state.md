# Eureka AIDE Project State

- Target repo identity: `julesc013/eureka`.
- Project summary: Eureka is a local-first live research search engine and temporal object-resolution layer for turning vague digital-object needs into provenance-preserving discoveries, observations, Preview Index records, and later reviewed knowledge.
- Current product task: `EUREKA-REAL-LIVE-SEARCH-HUNT-00`.
- Current objective: arbitrary live query -> immediate transient web leads -> deeper Hunt -> safe page inspection -> durable local Preview Index -> restart -> local search.
- Current implementation posture: milestones 1 and 2 are present, milestone 3 is partial, and milestones 4 through 6 remain incomplete.
- Local live provider calls: experimental, bounded, operator opt-in, and available only through explicit `--live` command/server modes with local credentials such as `BRAVE_SEARCH_API_KEY` or `BRAVE_API_KEY`.
- Public live fanout: disabled. Public exposure, tunnels, launch, public mutation, reviewed/master mutation, and production-readiness claims remain forbidden.
- Provider retention boundary: Brave Search Results are transient SearchLeads; do not persist provider URLs, snippets, ranks, raw responses, or API credentials. Durable local indexing must come from independently fetched, policy-approved SourceObservations.
- Incomplete product work: safe fetch, robots/SSRF policy, extraction, SQLite/FTS Preview Index persistence, restart retrieval proof, real budgeted Hunt, and unseen-query acceptance.
- Human acceptance: blocked until all six live Search/Hunt milestones pass.
- Source of truth: product truth remains in `contracts/`, `runtime/`, accepted architecture docs, and the current queue/task packet. This memory file is only a compact pointer surface.
- Token rule: do not paste long chat history or full repo docs into prompts. Generate compact target-local packets under `.aide/context/` and cite repo paths when more context is needed.
