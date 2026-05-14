# Dependency Matrix

- Local Appliance: upstream_required before HUNT-01 — HUNT must run through explicit instance, service, workbench, stores, workers, and eval harness.
- WorkUnit queue: upstream_required before HUNT-06 — Hunts create background work only through the WorkUnit queue.
- local worker runner: upstream_required before HUNT-07 — Deterministic workers execute safe local hunt WorkUnits.
- reviewed public index: upstream_required before HUNT-01 — Reviewed-index search is always checked before hunt escalation.
- evidence ledger: upstream_required before HUNT-05 — Candidates must remain evidence candidates until reviewed.
- review queue: upstream_required before HUNT-05 — Promotion requires review decisions.
- auto-test harness: upstream_required before HUNT-08 — Hunt behavior must be testable as commands.
- SYN: downstream_consumer before after HUNT-04 or HUNT-06 — SYN may generate SearchNeed and WorkUnit seeds, not evidence.
- F0: downstream_consumer before after HUNT baseline or operator override — F0 extraction should consume HUNT WorkUnits where applicable.
- G: downstream_consumer before after HUNT-04 — G consumes exhaustion, near-miss, ranking, and explanation records.
- H source expansion: downstream_consumer before after HUNT-06 — H source expansion runs through hunt/source-probe WorkUnits.
- K AI assist: downstream_consumer before after HUNT-11 — K consumes exhaustion reports and returns candidate-only outputs.
