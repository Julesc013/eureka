# UI Contracts

`contracts/ui/` holds shared view-model and UI contract assets that surfaces can govern together without reaching into runtime implementation detail.

These files are shared between web and native surfaces. In the normal path they align to the gateway public API boundary rather than to engine internals or app-shell behavior.

Current bootstrap shared models cover:

- `WorkbenchSession` for exact-resolution job state and object summaries
- `SearchResults` for deterministic search result lists and structured absence reports
- `ResolutionActions` for bounded action availability and manifest-export affordances
