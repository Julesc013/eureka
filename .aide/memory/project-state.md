# Eureka AIDE Project State

- Target repo identity: `julesc013/eureka`.
- Project summary: Eureka is a universal archive-resolution layer, or Software Time Machine, for resolving vague digital-object requests into evidence-backed actionable units.
- Current pilot: Q22 AIDE Lite import pilot in Eureka.
- Immediate goal: generate a compact next Eureka task packet from current repo state and prove it is materially smaller than a naive prompt baseline.
- Source of truth: full Eureka doctrine, architecture, contracts, and validation lanes remain in repo docs and inventories. This memory is only a compact pointer surface, not a pasted doctrine archive.
- Deferred surfaces: Eureka product feature changes, gateway/provider work, live model routing, autonomous loops, local model setup, MCP/A2A, semantic cache, vector DB, provider billing, and exact tokenizer work.
- Token rule: do not paste long chat history or full repo docs into prompts. Generate compact target-local packets under `.aide/context/` and cite repo paths when more context is needed.
- Validation baseline for Q22: `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, source pack `pack-status`, Q21 `import-pack --dry-run`, `.aide.local/` ignore check, `git diff --check`, and AIDE Lite `doctor` after memory initialization.
- Next intended task: use `.aide/context/latest-task-packet.md` to audit the current Eureka repo state and produce one bounded, reviewable next implementation task without product-code changes during the pilot.
