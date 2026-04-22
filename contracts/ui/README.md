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
- `BundleInspection` for local bootstrap readback of previously exported deterministic bundles, any recovered bootstrap resolved-resource identity, and bounded evidence summaries
- `StoredExports` for local bootstrap storage, listing, retrieval of deterministic exported artifacts, associated bootstrap resolved-resource identity, and bounded evidence summaries

This shared-contract layer now carries the first bounded provenance and evidence seam, the first bounded comparison and disagreement seam, the first bounded object/state timeline seam, and the first bounded absence-reasoning seam. It is not a final provenance graph, trust model, object identity model, merge contract, truth-selection engine, or diagnostic engine.
