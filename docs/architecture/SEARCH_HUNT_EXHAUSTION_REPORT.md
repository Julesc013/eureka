# Search Hunt Exhaustion Report

Search Hunt exhaustion reports are deterministic local explanations of what a Search Hunt Session has checked and what remains deferred. They are generated from the explicit Local Appliance instance, the reviewed public index, the Search Hunt session store, transition history, and active steering preferences.

The report is not a search result, evidence acceptance, source approval, or absence proof. It records local current-index state only and keeps future work as categories rather than executable work.

## Sections

- `query_summary`: hunt id, query, normalized query, intent, destination, and current hunt state.
- `checked_layers`: reviewed public index, local search summary, local absence report, hunt history, and steering preferences.
- `result_state`: reviewed result count, candidate count, near-miss count when locally available, absence state, and confidence class.
- `unchecked_or_deferred_layers`: source probes, WorkUnits, extraction, broader connectors, synthetic query foundry, ranking/identity merge, AI escalation, packs, and hosted index.
- `blocked_by_policy`: disabled source, work, extraction, model, external search, payload action, and index mutation boundaries.
- `recommended_next_actions`: future SearchNeed, work queue, source policy, extraction, synthetic query/eval, and escalation categories.
- `limitations`, `warnings`, and `non_claims`: the report’s safety boundary.

## Boundary

HUNT-04 persists reports and exposes them through CLI, local API, and the workbench. It does not create WorkUnits, run source probes, execute background workers, call model providers, mutate review decisions, rebuild indexes, or mutate public/master indexes.
## SearchNeed Handoff

HUNT-05 consumes exhaustion reports to create SearchNeeds. The exhaustion report supplies local result state, checked layers, deferred layers, blocked policy entries, and recommended future work categories.

The handoff does not turn an exhaustion report into proof. It only preserves local/current-index context for future operator-gated work.
## Agent Research Input

The exhaustion report is the required local context source for disabled agent research task drafts. A draft may copy checked layers, deferred layers, blocked policy entries, local absence state, steering preferences, and query summary fields. The draft remains non-executable and cannot be treated as evidence or truth.
