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

Current status within this stage: twenty-two local deterministic thin slices now exist in the Python stdlib bootstrap lane. The first proved fixture input to engine to gateway bounded-job flow. The second moved governed synthetic fixture access behind a local connector-shaped source path and proved ingest, extract, normalize, engine resolve, and gateway job flow without introducing real external connectors. The third added a transport-neutral public submit and read boundary plus shared workbench-session mapping without introducing real HTTP serving or UI shells. The fourth added deterministic search over the small governed synthetic corpus plus a transport-neutral public search boundary and shared search-results view model. The fifth added bounded engine action behavior plus a transport-neutral public action boundary for deterministic resolution-manifest export. The sixth added a deterministic portable resolution-bundle export under `runtime/engine/snapshots/` plus the corresponding public bundle-export seam. The seventh added deterministic bundle readback and inspection under `runtime/engine/snapshots/` plus a separate public bundle inspection boundary. The eighth added a deterministic local content-addressed store under `runtime/engine/store/` plus public storage, listing, and readback boundaries for exported artifacts. The ninth hardened the path with a bootstrap deterministic `resolved_resource_id` that now propagates across resolution, search, export, storage, inspection, and surface projection. The tenth added the first non-web CLI surface under `surfaces/native/cli/`. The eleventh added a narrow repo-local architecture-boundary checker for the current Python import layering. The twelfth added the first local stdlib machine-readable HTTP API slice over the same transport-neutral public boundary. The thirteenth added the first bounded real external-source connector slice by normalizing recorded GitHub Releases fixtures into the same deterministic engine, gateway, and surface path. The fourteenth added the first bounded provenance and evidence seam by carrying compact source-backed evidence summaries through normalize, resolution, export, storage, inspection, and current surfaces. The fifteenth added the first bounded comparison and disagreement seam by comparing two resolved targets side by side and preserving evidence per side through the public boundary plus current surfaces. The sixteenth added the first bounded object/state timeline seam by grouping multiple bounded states under one bootstrap `subject_key`, ordering them deterministically, and surfacing the ordered listing through the public boundary plus current surfaces without finalizing object identity semantics. The seventeenth added the first bounded absence-reasoning seam by explaining exact-resolution misses and deterministic search no-result cases with checked source-family summaries, compact near matches, and bounded next steps through the public boundary plus current surfaces without finalizing diagnostic, ranking, or trust semantics. The eighteenth added the first bounded representation and access-path seam by preserving multiple known source-backed representation summaries for one resolved target through normalize, exact resolution, public boundaries, and current surfaces without finalizing download, install, import, restore, or representation-selection semantics. The nineteenth added the first bounded compatibility seam by evaluating one resolved target against one bootstrap host profile preset, surfacing compact reasons plus honest `unknown` outcomes through the public boundary plus current surfaces without finalizing compatibility, installer, or runtime-routing semantics. The twentieth added the first bounded action-routing seam by turning one resolved target, bounded representations, optional host-aware compatibility, and bounded local export/store context into explicit recommended, available, and unavailable next steps through the public boundary plus current surfaces without finalizing execution, installer, or workflow-policy semantics. The twenty-first added the first bounded user-strategy seam by letting the same resolved target produce different explicit action emphasis under a small fixed strategy set, while preserving the same underlying identity, evidence, and representation truth through the public boundary plus current surfaces. The twenty-second adds the first bounded representation-selection and handoff seam by selecting one preferred bounded representation plus explicit alternatives shaped by optional host and strategy input, while preserving the same underlying identity, evidence, and representation truth through the public boundary plus current surfaces.

## Stage 3: Surface Skeletons

- add the initial web workbench shell against gateway public contracts
- add native shell scaffolding with offline-path boundaries still explicitly gated
- add basic cross-component verification paths

Current status within this stage: `surfaces/web/` now contains the first compatibility-first exact-resolution workbench page, the first deterministic search-and-absence page, the first bounded subject-state page, the first bounded representations page, the first bounded compatibility page, the first bounded handoff page, the first bounded action-plan page, dedicated bounded miss-explanation pages, a bounded action panel plus manifest-export and bundle-export routes for resolved targets, a stored-exports section plus local-store routes for deterministic stored artifacts, a compatibility-first bundle inspection page, and the first local stdlib machine-readable HTTP API slice for the same bounded capabilities. `surfaces/native/cli/` now provides the first non-web surface proof, including bounded subject-state listing, bounded miss-explanation commands, bounded representations listing, bounded handoff evaluation, bounded action-plan evaluation, bounded strategy-aware action-plan evaluation, and bounded compatibility evaluation. These slices are stdlib-only, local-only, consume transport-neutral gateway boundaries plus shared surface view models without importing engine internals directly, and now show bounded source-family visibility, bounded evidence summaries, bounded object/state grouping, bounded absence reasoning, bounded representation and access-path summaries, bounded representation-selection and handoff guidance, bounded action-routing recommendations, bounded strategy-aware recommendation emphasis, plus bounded host-profile compatibility verdicts for both synthetic fixtures and recorded GitHub Releases-backed results.

## Stage 4: Bounded Product Work

- begin software-first resolution, preservation, and reconstruction implementation
- add real evidence handling, compatibility reasoning, and snapshot workflows
- expand only where contract governance and architectural boundaries already exist

Out of scope for bootstrap: finalized runtime semantics, mature connector coverage, ranking systems, release automation, retrieval strategy expansion, and native runtime embedding beyond scaffolding.
