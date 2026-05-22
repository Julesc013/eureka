# Resolution Run Kernel

The Resolution Run Kernel is the headless behavior layer for Eureka search
flows. It creates a run, records commands and events, schedules WorkUnit-shaped
dry-run plans, builds result lane snapshots, and emits coverage reports.

Surfaces do not own resolution behavior:

- Workbench renders rich operator projections.
- API/CLI/TUI/native adapters project the same packets.
- Source-family adapters feed the kernel through governed WorkUnit and result
  lane seams.

The G0/F0/SCOUT/DOMAIN/SYN/IA-HUNT foundations remain inputs to the kernel. The
kernel does not replace review, evidence, source cache, or index authority.

Foundation boundaries:

- dry-run by default
- no live source calls
- no downloads, extraction, execution, or model/provider calls
- no accepted evidence, reviewed records, or identity merges
- no operator, public, or master index mutation
- no production or public launch claim

Future adapters may add filesystem or SQLite persistence, browser/API
projection, snapshot relay, and explicit local apply gates after review.
