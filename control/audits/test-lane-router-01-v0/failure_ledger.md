# Failure Ledger

The failure ledger records current active failures as first-class work items.

Current active entries are `fixed_pending_full` Search Hunt queue-handoff
failures from the last result-lane closeout discovery run. They are not ignored:
failed-first mode selects their rerun commands, and promotion mode refuses while
they remain active.

