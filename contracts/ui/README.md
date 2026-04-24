# UI Contracts

`contracts/ui/` holds shared view-model and UI contract assets that surfaces can govern together without reaching into runtime implementation detail.

These files are shared between web and native surfaces. In the normal path they align to the gateway public API boundary rather than to engine internals or app-shell behavior.

Current bootstrap shared models cover:

- `WorkbenchSession` for exact-resolution job state, object summaries, and bootstrap resolved-resource identity
- `SearchResults` for deterministic search result lists, bootstrap resolved-resource identity, bounded source summaries, and structured absence reports
- `AbsenceReport` for bounded miss explanations, checked source-family summaries, compact near matches, and bootstrap next-step hints
- `ResolutionActions` for bounded action availability plus bootstrap resolved-resource identity for the current resolved target
- `Comparison` for side-by-side left/right summaries, explicit agreements and disagreements, and bounded evidence preserved per side
- `SubjectStates` for one bootstrap subject summary plus an ordered state list that preserves compact source and evidence summaries per state
- `Representations` for one resolved target's bounded representation and access-path list, including compact access kind plus source-family summaries without implying final download or install behavior
- `Compatibility` for one resolved target evaluated against one bootstrap host profile preset, including compact verdict reasons and honest `unknown` outcomes
- `RepresentationSelection` for one resolved target's bounded preferred, available, unsuitable, and unknown handoff choices, including compact host-profile, strategy-profile, compatibility, and source context without implying downloads, installers, or runtime launches
- `Acquisition` for one resolved target plus one explicitly chosen representation, including compact fetched, unavailable, and blocked outcomes without implying live downloads, installers, or restore/import behavior
- `Decomposition` for one resolved target plus one explicitly chosen representation, including compact package-member listings for supported bounded formats and explicit unsupported or unavailable outcomes without implying broad extraction, installers, import, or restore behavior
- `MemberAccess` for one resolved target plus one explicitly chosen representation and member path, including compact preview or readback results plus explicit unsupported, unavailable, and blocked outcomes without implying extraction-to-disk, installers, import, or restore behavior
- `ActionPlan` for one resolved target's bounded recommended, available, and unavailable next-step actions, including compact host-profile, compatibility, strategy-profile, and representation context without implying execution, installer, runtime-routing, or personalization behavior
- `ResolutionRun` for synchronous local exact-resolution and deterministic-search investigation records, including checked sources plus current result or absence summaries without implying worker queues, streaming phases, or query-planner semantics
- `BundleInspection` for local bootstrap readback of previously exported deterministic bundles, any recovered bootstrap resolved-resource identity, and bounded evidence summaries
- `StoredExports` for local bootstrap storage, listing, retrieval of deterministic exported artifacts, associated bootstrap resolved-resource identity, and bounded evidence summaries

This shared-contract layer now carries the first bounded provenance and evidence seam, the first bounded comparison and disagreement seam, the first bounded object/state timeline seam, the first bounded absence-reasoning seam, the first bounded representation/access-path seam, the first bounded compatibility seam, the first bounded action-routing seam, the first bounded user-strategy seam, the first bounded representation-selection and handoff seam, the first bounded acquisition and fetch seam, the first bounded decomposition and package-member seam, the first bounded member-readback and preview seam, and the first bounded resolution-run seam. It is not a final provenance graph, trust model, object identity model, representation, acquisition, decomposition, member-extraction, action model, handoff or runtime-launch model, merge contract, compatibility oracle, truth-selection engine, worker queue, query planner, personalization system, diagnostic engine, extraction framework, or execution policy engine.
