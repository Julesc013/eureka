# File Divergence

Diff summary from `origin/main..HEAD` shows `555` changed files, with the local safety branch adding Track B runtime/docs/policies/examples/tests and removing remote OBS seed/review artifacts relative to `origin/main`.

Diff summary from `HEAD..origin/main` shows the inverse: remote OBS seed/review artifacts appear as additions and local Track B artifacts appear as deletions.

## Local-Heavy Areas

- Track B runtime modules under `runtime/local/foundry/`.
- Track B scripts under `scripts/`.
- Track B tests under `tests/runtime/`, `tests/operations/`, and `tests/contracts/`.
- Track B policies under `control/inventory/`.
- Track B audit packs through TRACK-B-23.
- Pack builder/export, reviewed public index rebuild, and candidate promotion dry-run docs/examples.
- REPO-SYNC-03 preservation audit pack.

## Remote-Heavy Areas

- OBS-AGENT-04 through OBS-AGENT-07 audit packs.
- SearchNeed seed and WorkUnit seed contracts.
- OBS synchronization and human review packet inventories.
- OBS seed/review scripts and tests.
- OBS operations docs and observation review examples.

## Overlap Since Merge Base

Local changed paths since base: `515`

Remote changed paths since base: `176`

Overlapping changed paths: `68`

Overlap groups:

- `contracts/query`: 1
- `control/audits`: 27
- `control/inventory`: 8
- `docs/operations`: 4
- `examples/observation_candidates`: 11
- `examples/review/observation_reviews`: 4
- `scripts/*`: 8
- `tests/contracts`: 1
- `tests/operations`: 4

## AIDE State

The `.aide/context/*` and `.aide/evals/runs/latest-golden-tasks.*` files differ between tips. These are operational metadata and should be reviewed during convergence so stale packets do not overwrite newer task context.

## Generated Artifact Notes

No `site/dist` mutation was observed by this audit. No public index or master-index mutation was performed by this task.
