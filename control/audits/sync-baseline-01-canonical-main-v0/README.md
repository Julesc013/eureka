# SYNC-BASELINE-01 - Canonical Main Baseline

This audit records the baseline reset after OBS, Track B, repo sync recovery, and SYNC-GUARD-01 were unified.

## Result

- Local `main` is the integration branch.
- Remote `origin/main` is the canonical branch.
- `task/sync-guard-01` was merged into `main`.
- The old preservation branch is retained as historical evidence and is already represented in main history.
- Full unittest discovery passed on `main`.
- AIDE Lite checks passed except WARN-only verification references with zero errors.

## Scope

This is a control baseline. It did not add product runtime behavior, approve sources, execute WorkUnits, enable connectors, create public truth, or mutate the master index.

## Files

- `baseline_report.json`
- `branch_inventory.md`
- `merged_branch_report.md`
- `validation_matrix.md`
- `test_report.md`
- `aide_state_report.md`
- `resync_instructions.md`
- `next_steps.md`
