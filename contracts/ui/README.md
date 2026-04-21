# UI Contracts

`contracts/ui/` holds shared view-model and UI contract assets that surfaces can govern together without reaching into runtime implementation detail.

These files are shared between web and native surfaces. In the normal path they align to the gateway public API boundary rather than to engine internals or app-shell behavior.

Current bootstrap shared models cover:

- `WorkbenchSession` for exact-resolution job state, object summaries, and bootstrap resolved-resource identity
- `SearchResults` for deterministic search result lists, bootstrap resolved-resource identity, and structured absence reports
- `ResolutionActions` for bounded action availability plus bootstrap resolved-resource identity for the current resolved target
- `BundleInspection` for local bootstrap readback of previously exported deterministic bundles and any recovered bootstrap resolved-resource identity
- `StoredExports` for local bootstrap storage, listing, retrieval of deterministic exported artifacts, and associated bootstrap resolved-resource identity
