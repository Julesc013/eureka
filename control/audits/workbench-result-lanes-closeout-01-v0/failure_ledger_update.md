# Failure Ledger Update

The two original Search Hunt `fixed_pending_full` failures were rerun first and passed:

- `tests.operations.test_search_hunt_closeout`
- `tests.operations.test_search_hunt_track`

They were updated to `fixed_confirmed`.

New full-discovery failures:

- `full-discovery-2026-05-21-contract-taxonomy-testing-selection-result`: reproduced. Repair requires updating the R0-03A contract taxonomy inventory, which is outside this closeout's allowed paths.
- `full-discovery-2026-05-21-local-appliance-repo-health`: fixed in AIDE repo-health metadata and passed focused rerun. It remains `fixed_pending_full` until another full discovery confirms it.

IA-HUNT-BRIDGE-00 remains blocked.
