# Track Plan

- HUNT-00 — Search Hunt track planning over Local Appliance: Define the investigation spine and gates before runtime work.
- HUNT-01 — Search Hunt Session runtime: Persist Search Hunt Session records with explicit lifecycle state.
- HUNT-02 — Search Hunt UI state in Local Workbench: Expose hunt state in the local workbench without adding unsafe mutation.
- HUNT-03 — Pause, resume, cancel, and steer commands: Add operator commands for controlled hunt transitions.
- HUNT-04 — Hunt exhaustion report: Record checked layers, near misses, blocked sources, and limitations.
- HUNT-05 — Hunt-to-SearchNeed pipeline: Create reviewed SearchNeed candidates from hunt state.
- HUNT-06 — Hunt-to-WorkUnit pipeline: Create bounded WorkUnits from hunt needs through the queue.
- HUNT-07 — Background hunt runner over deterministic local workers: Run deterministic local hunt workers without source probes by default.
- HUNT-08 — Workbench hunt integration and smoke tests: Smoke-test workbench hunt status and controls.
- HUNT-09 — Agent research task contract, provider disabled: Define agent research task contract while providers remain disabled.
- HUNT-10 — Deterministic hunt replay harness: Replay hunt sessions deterministically for regression tests.
- HUNT-11 — Bounded AI escalation gate, disabled by default: Add disabled-by-default AI escalation gate over exhaustion reports.
- HUNT-12 — Search Hunt closeout and SYN/F0 handoff: Close HUNT and hand off to SYN/F0/G/H/K tracks.
