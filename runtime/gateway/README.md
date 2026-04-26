# Gateway

`runtime/gateway/` is the runtime implementation area for gateway behavior.

Boundary notes:

- gateway depends on governed contracts plus `runtime/engine/interfaces/public/**` and `runtime/engine/interfaces/service/**`
- gateway public product contracts live under `contracts/gateway/public_api`
- the `public_api/` directory here is for runtime implementation support, not for canonical contract definition

Current thin-slice behavior:

- transport-neutral public submit and read boundary over an in-memory job service
- transport-neutral public search boundary over a bounded normalized corpus composed from synthetic fixtures, recorded GitHub Releases records, recorded Internet Archive-like fixtures, and committed local bundle fixtures
- transport-neutral public query-planner boundary for deterministically compiling a bounded set of raw-query families into shared `ResolutionTask` envelopes
- transport-neutral public local-index boundary for building, inspecting, and querying a bootstrap local SQLite index over the current bounded corpus
- transport-neutral public local-tasks boundary for creating, reading, and listing synchronous bootstrap local task records over a caller-provided local task-store root
- transport-neutral public resolution-runs boundary for synchronous exact-resolution, deterministic-search, and planned-search investigation records persisted under a caller-provided local bootstrap run-store root
- transport-neutral public resolution-memory boundary for explicitly creating, reading, and listing local resolution-memory records derived from persisted completed runs under a caller-provided local bootstrap memory-store root
- transport-neutral public absence boundary for explaining bounded exact-resolution and deterministic search misses
- transport-neutral public comparison boundary for side-by-side comparison of exactly two resolved targets with explicit agreements and disagreements
- transport-neutral public subject/state boundary for listing bounded ordered states under one bootstrap `subject_key`
- transport-neutral public action boundary for bounded manifest and bundle discovery and export
- transport-neutral public representations boundary for listing bounded known representations and access paths for one resolved target
- transport-neutral public compatibility boundary for evaluating one resolved target against one bootstrap host profile preset
- transport-neutral public handoff boundary for selecting one bounded preferred representation plus explicit alternatives for one resolved target, optionally shaped by one bootstrap host profile preset and one bootstrap strategy profile
- transport-neutral public acquisition boundary for fetching one explicitly chosen bounded representation payload for one resolved target
- transport-neutral public decomposition boundary for inspecting one explicitly chosen fetched bounded representation into a compact member listing
- transport-neutral public member-access boundary for reading one explicitly chosen bounded member from one explicitly chosen fetched representation
- transport-neutral public action-plan boundary for building bounded recommended, available, and unavailable next steps for one resolved target, optionally shaped by one bootstrap host profile preset plus one bootstrap strategy profile
- transport-neutral public stored-exports boundary for local deterministic artifact storage, listing, and retrieval
- transport-neutral public bundle inspection boundary for local bootstrap readback of exported bundles
- submit returns an accepted public envelope while read returns the current bounded job envelope
- deterministic job envelopes for known and unknown bounded targets from the mixed demo corpus
- deterministic search results or a structured absence report for bounded queries
- deterministic manifest and bundle export for known synthetic or GitHub Releases-backed targets plus blocked export responses for misses
- deterministic local stored-export identity, listing, and readback through a caller-provided store root
- deterministic local bundle inspection without live fixture dependence
- bootstrap deterministic `resolved_resource_id` propagation across resolution, search, action, storage, inspection, and shared-surface mappings
- bounded source-family visibility propagated across resolution, search, export, storage, inspection, and shared-surface mappings where the public boundary provides it
- bounded checked-source visibility propagated across synchronous resolution runs and shared-surface mappings where the public boundary provides it
- bounded query-plan summaries propagated across the public query-planner boundary and into planned-search resolution runs where the public boundary provides them
- bounded local-index summaries propagated across the public local-index boundary and shared-surface mappings where the public boundary provides them
- bounded local-task summaries propagated across the public local-tasks boundary and shared-surface mappings where the public boundary provides them
- bounded resolution-memory summaries propagated across the public resolution-memory boundary and shared-surface mappings where the public boundary provides them
- bounded evidence summaries propagated across resolution, search, export, storage, inspection, and shared-surface mappings where the public boundary provides them
- bounded comparison and disagreement summaries propagated across the public boundary and shared-surface mappings without implying merge logic or trust selection
- bounded subject/state grouping propagated across the public boundary as a compact timeline/list seam without implying a final global object identity or temporal graph
- bounded absence reports propagated across the public boundary as compact miss explanations without implying ranking, trust reasoning, or a final diagnostic engine
- bounded representation and access-path summaries propagated across the public boundary and shared-surface mappings without implying final download, install, import, restore, or representation-selection semantics
- bounded compatibility verdicts propagated across the public boundary and shared-surface mappings without implying a final compatibility oracle, installer, or runtime-routing engine
- bounded representation-selection and handoff summaries propagated across the public boundary and shared-surface mappings without implying downloads, installers, launches, or final runtime-routing semantics
- bounded acquisition results propagated across the public boundary and shared-surface mappings without implying live downloads, installers, launches, restore flows, or final download semantics
- bounded decomposition results propagated across the public boundary and shared-surface mappings without implying broad extraction tooling, installers, import, restore, or final package semantics
- bounded member-access results propagated across the public boundary and shared-surface mappings without implying extraction-to-disk, installers, import, restore, or final package-management semantics
- bounded action plans propagated across the public boundary and shared-surface mappings without implying execution, installer, launcher, final policy-engine behavior, or a final personalization model
- gateway composes with engine service interfaces over normalized records and local bootstrap resolution-run records and does not read governed fixtures directly
- shared workbench-session, search-results, representations, resolution-actions, stored-exports, and bundle-inspection mappings are exercised without implementing web or native shells
- no broker, relay, async worker, background scheduler, auth, or streaming transport implementation
This slice proves the public boundary shape without implying that async gateway infrastructure already exists. Local persistence now exists only for deterministic exported artifacts, synchronous bootstrap resolution-run JSON records, explicit bootstrap resolution-memory JSON records, synchronous bootstrap local-task JSON records, and a caller-provided bootstrap local SQLite index behind engine-owned services. The current `resolved_resource_id` is intentionally a bootstrap deterministic seam, not a final global identity registry or merge model.
