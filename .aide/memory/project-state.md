# Eureka AIDE Project State

- Target repo identity: `julesc013/eureka`.
- Project summary: Eureka is a universal archive-resolution layer, or Software Time Machine, for resolving vague digital-object requests into evidence-backed actionable units.
- Current pilot: EUREKA-AIDE-REAL-01 adds the first bounded AIDE-driven Eureka repo-health report after the final handoff.
- Immediate goal: keep future Eureka Codex/GPT work grounded in repo-local health, handoff, task-packet, validation, and queue evidence instead of external chat history.
- Source of truth: full Eureka doctrine, architecture, contracts, and validation lanes remain in repo docs and inventories. This memory is only a compact pointer surface, not a pasted doctrine archive.
- Deferred surfaces: Eureka product feature changes, gateway/provider work, live model routing, autonomous loops, local model setup, MCP/A2A, semantic cache, vector DB, provider billing, and exact tokenizer work.
- Token rule: do not paste long chat history or full repo docs into prompts. Generate compact target-local packets under `.aide/context/` and cite repo paths when more context is needed.
- Validation baseline for EUREKA-AIDE-REAL-01: Git state checks, `.aide.local/` ignore check, AIDE Lite `doctor`, `validate`, `test`, `selftest`, `verify`, `eval list`, `eval run`, `adapter validate`, packet refresh, token estimate, strict secret scan, JSON validation, and `scripts/check_architecture_boundaries.py`.
- Next intended task: use `.aide/context/latest-task-packet.md` for `EUREKA-CONVERGE-01 - Track and prompt queue convergence audit`.
