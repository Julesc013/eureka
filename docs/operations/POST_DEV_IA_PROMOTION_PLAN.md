# Post Dev IA Promotion Plan

After the dev baseline is promoted to main, the repo should move into Workbench
Foundation rather than new source expansion. This plan is deferred until the
blocked promotion review has green or explicitly accepted gates.

Current blocker:

- `DEV-AND-IA-PROMOTION-BLOCKER-01` must resolve or explicitly reclassify the
  full-discovery failures in candidate-index, contract taxonomy,
  runtime/source-observation leakage, and HUNT/LOCAL promotion-state lanes.

The promoted state includes:

- IA metadata-only local vertical slice.
- Repo layout canon and validator.

The promoted state does not include:

- not production readiness
- not public launch readiness
- not full Archive.org integration
- public IA fanout
- downloads or uploads
- extraction
- AI/model-provider calls
- deployment
- not marketplace/app-store readiness
- Workbench implementation
- SYN implementation

## Sequence

1. `WORKBENCH-FOUNDATION-00` - Mission Control doctrine, route/view matrix, and
   projection model.
2. `SEARCH-INTERACTION-00` - search interaction contract and state machine.
3. `WORKBENCH-RESULT-LANES-01` - reviewed, candidate, source-cache, IA metadata,
   review, absence, blocked, and WorkUnit lanes.
4. `IA-HUNT-BRIDGE-00` - bridge IA metadata candidates into Hunt/WorkUnit lanes.
5. `SYN-00` - pressure-test the real Workbench and interaction contract.

This plan treats the Workbench as the internal superset of the final product,
with public and native products as later restricted projections.
