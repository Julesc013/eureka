# Eureka AIDE Project State

- Target repo identity: `julesc013/eureka`.
- Project summary: Eureka is a universal archive-resolution layer, or Software Time Machine, for resolving vague digital-object requests into evidence-backed actionable units.
- Current pilot: EUREKA-AIDE-SELFTEST-01 repaired the imported AIDE Lite temp-fixture fallback discovered during Q26 handover.
- Immediate goal: preserve passing Eureka-local AIDE Lite `test` and `selftest` while handing off to the first Eureka-specific golden-task repair.
- Source of truth: full Eureka doctrine, architecture, contracts, and validation lanes remain in repo docs and inventories. This memory is only a compact pointer surface, not a pasted doctrine archive.
- Deferred surfaces: Eureka product feature changes, gateway/provider work, live model routing, autonomous loops, local model setup, MCP/A2A, semantic cache, vector DB, provider billing, and exact tokenizer work.
- Token rule: do not paste long chat history or full repo docs into prompts. Generate compact target-local packets under `.aide/context/` and cite repo paths when more context is needed.
- Validation baseline for EUREKA-AIDE-SELFTEST-01: Git state checks, `.aide.local/` ignore check, AIDE Lite `doctor`, `validate`, `test`, `selftest`, `verify`, `eval run`, `adapter validate`, packet regeneration, token estimate, strict secret scan, and `scripts/check_architecture_boundaries.py`.
- Next intended task: use `.aide/context/latest-task-packet.md` for `EUREKA-AIDE-GOLDEN-01 - Add Eureka-specific AIDE golden tasks`.
