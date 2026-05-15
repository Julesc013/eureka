# Search Hunt Model

A search can become an investigation when the reviewed local index is absent, weak, ambiguous, stale, or policy-blocked. A Search Hunt Session is governed state, not truth. It records query context, checked layers, near misses, limitations, and future work. Candidates, WorkUnits, AI output, and source observations remain non-truth until reviewed evidence-backed records enter the reviewed index.

HUNT-01 persists the first Search Hunt Session runtime. A persisted session still remains non-truth: it can record reviewed-index search summaries, local/current-index absence summaries, limitations, warnings, and transition history, but it cannot accept evidence or mutate reviewed records.

HUNT-02 exposes that persisted state in the Local Appliance workbench. The UI is read-only and separates reviewed local index summaries, local/current-index absence, checked layers, unchecked/deferred layers, warnings, limitations, and unavailable future actions.

HUNT-03 adds operator-gated controls for local hunt state. Pause, resume, cancel, block, wait, complete, fail, and steering preferences are command history, not investigation execution. They do not create WorkUnits, run source probes, call models, accept evidence, or mutate indexes.

HUNT-04 adds deterministic exhaustion reports. A report explains local/current-index checked layers, deferred layers, blocked policies, future action categories, limitations, and non-claims. It remains local explanation state and does not create WorkUnits, run source probes, call model providers, accept evidence, or mutate reviewed indexes.
## HUNT-05 SearchNeeds

Search Hunt Sessions can now produce local SearchNeeds after an operator-gated HUNT-05 pipeline step. A SearchNeed is durable demand state linked to the hunt and its local exhaustion report.

SearchNeeds do not create WorkUnits, execute probes, call model providers, accept evidence, or mutate indexes. They are the handoff from unresolved hunt state into future work planning.
## HUNT-06 WorkUnit Link

SearchNeeds can now produce deterministic WorkUnit plans and local queue records. These WorkUnits are local tasks, not truth or evidence. HUNT-06 queues local-safe work and blocks policy-gated future work; it does not run WorkUnits, source probes, extraction, or model/provider calls.

## HUNT-07 Background Runner

Search Hunt Sessions can now drive bounded background progress through deterministic local workers already allowed by LOCAL-09. The runner plans linked WorkUnits, runs only safe local worker kinds, records worker results, and preserves policy-blocked WorkUnits as blocked.

The runner does not run source probes, extraction, agent research, model/provider calls, acquisition actions, source sync, LAN workers, deployment, review mutation, or master-index mutation. A worker result remains local run state, not accepted truth or evidence.
## Workbench Integration Smoke

HUNT-08 proves the local Search Hunt loop through CLI, JSON API, and HTML workbench surfaces. The proof remains local and deterministic: Hunt command state, steering, exhaustion, SearchNeed creation, WorkUnit planning/creation, and safe background worker execution are visible without source probes, extraction, AI/model calls, deployment, or production/public launch claims.
