# Post Result Lanes Plan

Immediate validation follow-up: WORKBENCH-RESULT-LANES-VALIDATION-SPEED-01 - reduce full-discovery runtime and rerun the post-patch suite.

Product queue task after validation-speed follow-up: IA-HUNT-BRIDGE-00 - Connect IA metadata source work to Hunt, WorkUnits, and result lanes.

Planned sequence:

- IA-HUNT-BRIDGE-00
- SYN-00
- DOMAIN-00
- SCOUT-SCHEMA-00
- F0

Open boundaries:

- No IA-HUNT bridge has been implemented.
- No live IA calls are enabled.
- No source probes are enabled.
- No extraction, model/provider calls, downloads, uploads, deployment, public fanout, production readiness, or public launch readiness are claimed.
- Result lanes remain projections, not truth creation.

Closeout note:

- Full unittest discovery was rerun after result-lane runtime changes.
- Last run: 4784 tests in 2694.362s, failed with 2 stale Search Hunt queue-handoff allowlist failures for IA-HUNT-BRIDGE-00.
- The stale allowlists were patched after that run.
- Full discovery was not rerun again by operator request; the next prompt is expected to focus on validation speed before continuing the product queue.
