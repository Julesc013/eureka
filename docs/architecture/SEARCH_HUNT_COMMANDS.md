# Search Hunt Commands

HUNT-03 adds local operator commands for Search Hunt Sessions. Commands can pause, resume, cancel, block, mark waiting states, complete, fail, and record steering preferences. They change only local hunt state and local command/steering history.

Commands do not perform investigation work. They do not create WorkUnits, run workers, execute source probes, call model providers, mutate review decisions, rebuild indexes, mutate the public index, or mutate any master index.

## State Commands

State commands map onto the existing Search Hunt state machine. Invalid transitions fail closed. Repeated terminal transitions such as cancelling an already cancelled hunt are recorded idempotently where practical.

`block` and `fail` require a reason because they explain why future work is stopped or considered failed.

## Steering

Steering preferences record operator intent for future work. They are append-only command history plus active/inactive preference rows. Deactivation never silently deletes the original preference.

Steering is not evidence, source approval, rights clearance, safety clearance, truth acceptance, or authorization to download, crawl, scrape, extract, call models, or mutate indexes.

## Auth Boundary

Mutating command routes are localhost-only and operator-token-gated. LAN clients may read hunt pages when LAN read-only mode is enabled, but HUNT-03 command mutations return 403 for LAN clients.

## Exhaustion Report Command History

HUNT-04 records report generation in command history with no state change. That entry documents local report generation only. It does not authorize future work, source access, extraction, model/provider calls, or index mutation.
