# Dev To Main Promotion Blockers

`dev -> main` promotion remains blocked.

## Blockers

- No current external full-discovery summary for
  `3868150d89830256655a8c7d8ff3b1b7f3bebd82`.
- Queue index is stale relative to the current committed task chain.
- Public alpha corpus gate fails.
- Historical source/snapshot failure-family evidence must be refreshed before
  repair or waiver decisions.
- Manual promotion review has not accepted this current state.

## Required Before Promotion

1. Run `EXTERNAL-FULL-DISCOVERY-RUN-01`.
2. If red, repair current failure families.
3. Rerun external full discovery until current summary is green or a reviewed
   waiver exists.
4. Reassess promotion with current docs, queue, and validation evidence.
