# Import Report And Diff Model

The dry-run report summarizes candidate effects only. It does not compare
against authoritative runtime stores unless a later milestone approves that
boundary.

- source cache effects are candidate-only
- evidence ledger effects are candidate-only
- candidate/public/master index effects are future-only or blocked
- no accepted records are created
- no promotion decisions are created
- no destructive changes are possible

The `dry_run_effects` object records effect pack IDs and mutation impact counts
without creating runtime import state.
