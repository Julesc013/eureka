# Search Hunt Model

A search can become an investigation when the reviewed local index is absent, weak, ambiguous, stale, or policy-blocked. A Search Hunt Session is governed state, not truth. It records query context, checked layers, near misses, limitations, and future work. Candidates, WorkUnits, AI output, and source observations remain non-truth until reviewed evidence-backed records enter the reviewed index.

HUNT-01 persists the first Search Hunt Session runtime. A persisted session still remains non-truth: it can record reviewed-index search summaries, local/current-index absence summaries, limitations, warnings, and transition history, but it cannot accept evidence or mutate reviewed records.

HUNT-02 exposes that persisted state in the Local Appliance workbench. The UI is read-only and separates reviewed local index summaries, local/current-index absence, checked layers, unchecked/deferred layers, warnings, limitations, and unavailable future actions.

HUNT-03 adds operator-gated controls for local hunt state. Pause, resume, cancel, block, wait, complete, fail, and steering preferences are command history, not investigation execution. They do not create WorkUnits, run source probes, call models, accept evidence, or mutate indexes.

HUNT-04 adds deterministic exhaustion reports. A report explains local/current-index checked layers, deferred layers, blocked policies, future action categories, limitations, and non-claims. It remains local explanation state and does not create WorkUnits, run source probes, call model providers, accept evidence, or mutate reviewed indexes.
