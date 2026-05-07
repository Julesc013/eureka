# Eureka AIDE Project State

- Target repo identity: `julesc013/eureka`.
- Project summary: Eureka is a universal archive-resolution layer, or Software Time Machine, for resolving vague digital-object requests into evidence-backed actionable units.
- Current pilot: Q26 AIDE Lite handover review in Eureka after the Q22 import pilot and AIDE Q25 pack/importer repair.
- Immediate goal: approve controlled AIDE Lite use for the next bounded Eureka task and generate a compact handoff packet to repair the imported AIDE Lite selftest fixture fallback.
- Source of truth: full Eureka doctrine, architecture, contracts, and validation lanes remain in repo docs and inventories. This memory is only a compact pointer surface, not a pasted doctrine archive.
- Deferred surfaces: Eureka product feature changes, gateway/provider work, live model routing, autonomous loops, local model setup, MCP/A2A, semantic cache, vector DB, provider billing, and exact tokenizer work.
- Token rule: do not paste long chat history or full repo docs into prompts. Generate compact target-local packets under `.aide/context/` and cite repo paths when more context is needed.
- Validation baseline for Q26: Git state checks, `.aide.local/` ignore check, source pack `pack-status`, safe import dry-run, AIDE Lite `doctor`, `validate`, `snapshot`, `index`, `context`, `verify`, `review-pack`, `ledger`, `eval`, `route explain`, `adapter validate`, and `scripts/check_architecture_boundaries.py`.
- Next intended task: use `.aide/context/latest-task-packet.md` to make Eureka-local AIDE Lite `test` and `selftest` pass without importing broad AIDE `core/**` roots or changing Eureka product code.
