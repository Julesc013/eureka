# Roadmap

The roadmap is intentionally staged and bounded. Bootstrap work should make later implementation easier to govern, not attempt to deliver the full product in one pass.

## Stage 0: Bootstrap and Repo Contract

- establish the monorepo structure
- write founding documentation
- pin minimal AIDE repo-operating metadata
- create the initial contract, runtime, surface, test, and eval scaffolding

## Stage 1: Contract Hardening

- refine archive schema placeholders into governed draft contracts
- define the first public gateway contract set
- define shared UI contract and view-model boundaries
- add compatibility and migration rules for contract evolution

## Stage 2: Runtime Skeletons

- add engine interface boundaries without full product logic
- add gateway service boundaries and internal implementation seams
- scaffold connector adapters against `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, and `runtime/engine/interfaces/normalize/**`

Current status within this stage: seven local deterministic thin slices now exist in the Python stdlib bootstrap lane. The first proved fixture input to engine to gateway bounded-job flow. The second moved governed synthetic fixture access behind a local connector-shaped source path and proved ingest, extract, normalize, engine resolve, and gateway job flow without introducing real external connectors. The third added a transport-neutral public submit and read boundary plus shared workbench-session mapping without introducing real HTTP serving or UI shells. The fourth added deterministic search over the small governed synthetic corpus plus a transport-neutral public search boundary and shared search-results view model. The fifth added bounded engine action behavior plus a transport-neutral public action boundary for deterministic resolution-manifest export. The sixth added a deterministic portable resolution-bundle export under `runtime/engine/snapshots/` plus the corresponding public bundle-export seam. The seventh adds deterministic bundle readback and inspection under `runtime/engine/snapshots/` plus a separate public bundle inspection boundary.

## Stage 3: Surface Skeletons

- add the initial web workbench shell against gateway public contracts
- add native shell scaffolding with offline-path boundaries still explicitly gated
- add basic cross-component verification paths

Current status within this stage: `surfaces/web/` now contains the first compatibility-first exact-resolution workbench page, the first deterministic search-and-absence page, a bounded action panel plus manifest-export and bundle-export routes for resolved targets, and a compatibility-first bundle inspection page. These slices are stdlib-only, local-only, server-rendered, and consume transport-neutral gateway boundaries plus shared surface view models without importing engine internals.

## Stage 4: Bounded Product Work

- begin software-first resolution, preservation, and reconstruction implementation
- add real evidence handling, compatibility reasoning, and snapshot workflows
- expand only where contract governance and architectural boundaries already exist

Out of scope for bootstrap: finalized runtime semantics, mature connector coverage, ranking systems, release automation, retrieval strategy expansion, and native runtime embedding beyond scaffolding.
