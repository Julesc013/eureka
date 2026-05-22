# Local Workbench View Models

LOCAL-06 hardens the server-rendered workbench by making each page render from presentation-safe view models in `surfaces/web/workbench/local_html/view_models.py`.

## Shared Views

- `NonClaimBannerView` carries the local-only, localhost-only, read-only, reviewed-local-projection messages shown on every page.
- `CapabilityUnavailableView` lists unavailable capabilities such as WorkUnits, review/index maintenance UI, source probes, extraction, Search Hunt Sessions, LAN mode, and deployment.
- `ProvenanceRefView` carries source cache, evidence, review item, and review decision references when the public index record has them.

## Page Views

- `HomePageView` shows instance and index summary, warnings, limitations, and unavailable capabilities.
- `SearchPageView` shows the submitted query, reviewed local result count, local index limitations, and `SearchResultCardView` rows.
- `SearchResultCardView` includes record ID, title, description, source ID, source family, trust lane, provenance references, warnings, and limitations.
- `ObjectPageView` shows found/not-found state, normalized fields, safe searchable text excerpt, provenance references, warnings, and limitations.
- `SourcePageView` shows source-local record count and a local-scope notice. It does not imply global source coverage.
- `AbsencePageView` shows checked layers, unchecked/deferred layers, checked source references, limitations, and the non-claim that absence is not proof the artifact does not exist.
- `StatusPageView` shows instance ID, instance schema version, display-safe instance root, store manifest/store status, index status, migration state, server/LAN/deployment flags, warnings, and limitations.

View models do not carry store handles and do not expose mutation methods.
