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
- `ActionPlan` for one resolved target's bounded recommended, available, and unavailable next-step actions, including compact host-profile, compatibility, strategy-profile, and representation context without implying execution, installer, runtime-routing, or personalization behavior
- `BundleInspection` for local bootstrap readback of previously exported deterministic bundles, any recovered bootstrap resolved-resource identity, and bounded evidence summaries
- `StoredExports` for local bootstrap storage, listing, retrieval of deterministic exported artifacts, associated bootstrap resolved-resource identity, and bounded evidence summaries

This shared-contract layer now carries the first bounded provenance and evidence seam, the first bounded comparison and disagreement seam, the first bounded object/state timeline seam, the first bounded absence-reasoning seam, the first bounded representation/access-path seam, the first bounded compatibility seam, the first bounded action-routing seam, and the first bounded user-strategy seam. It is not a final provenance graph, trust model, object identity model, representation or action model, merge contract, compatibility oracle, truth-selection engine, personalization system, diagnostic engine, or execution policy engine.
