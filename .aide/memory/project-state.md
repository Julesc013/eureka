# Eureka AIDE Project State

- Target repo identity: `julesc013/eureka`.
- Project summary: Eureka is a local-first live research search engine and temporal object-resolution layer for turning vague digital-object needs into provenance-preserving discoveries, observations, Preview Index records, and later reviewed knowledge.
- Current product task: `EUREKA-REAL-LIVE-SEARCH-HUNT-00`.
- Current objective: arbitrary live query -> immediate transient web leads -> deeper Hunt -> safe page inspection -> durable local Preview Index -> restart -> local search.
- Current implementation posture: all six deterministic live Search/Hunt implementation milestones are present; real live acceptance is waiting on `DISCOVERY-BROKER-LIVE-CANARY-00`, which may use any healthy approved broad-web provider. Human product acceptance remains separate.
- Current hardening wave: `EUREKA-LIVE-PRODUCT-HARDENING-AND-ACCEPTANCE-WAVE-03` adds observability, recovery, performance baselines, Foundry operator controls, provider policy registry validation, portable local bundle rehearsal, canary closeout, human rehearsal, external full-discovery handoff, and a hardening audit.
- Local live provider calls: experimental, bounded, operator opt-in, and available only through explicit `--live` command/server modes with local broad-web credentials such as Brave or Mojeek keys.
- Public live fanout: disabled. Public exposure, tunnels, launch, public mutation, reviewed/master mutation, and production-readiness claims remain forbidden.
- Provider retention boundary: restrictive provider Search Results are transient SearchLeads; do not persist provider URLs, snippets, ranks, raw responses, or API credentials unless the provider manifest expressly permits it. Durable local indexing must come from independently fetched, policy-approved SourceObservations or explicitly allowed metadata.
- Remaining product gates: provider-neutral live canary, human usefulness acceptance, external full discovery, and hardening audit closeout.
- Human acceptance: blocked until the real live canary passes; automation must not fill in the operator verdict.
- Volatile capability source: `control/inventory/product/capability_state.json`.
- Source of truth: product truth remains in `contracts/`, `runtime/`, accepted architecture docs, and the current queue/task packet. This memory file is only a compact pointer surface.
- Token rule: do not paste long chat history or full repo docs into prompts. Generate compact target-local packets under `.aide/context/` and cite repo paths when more context is needed.
