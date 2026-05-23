# Resolution Run Contracts

Resolution-run contracts describe the portable headless orchestration layer that
connects search requests, commands, events, WorkUnits, lane snapshots, and
coverage reports.

The contracts do not define a browser, CLI, native, or API implementation.
Surfaces project these packets; the kernel owns behavior.

Foundation non-claims:

- no live source calls by default
- no downloads or extraction
- no model/provider calls
- no accepted evidence or reviewed records
- no operator, public, or master index mutation
- no production or public launch claim
