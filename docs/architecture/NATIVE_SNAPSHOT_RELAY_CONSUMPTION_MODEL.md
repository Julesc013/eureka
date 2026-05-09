# Native Snapshot Relay Consumption Model

Native clients consume local, public-safe representations:

- snapshot manifests and snapshot records
- relay fixture endpoint envelopes
- safe action manifests and blocked action reports
- citation, export, and acquisition manifests

This model keeps native clients separate from source resolution and truth acceptance. A native client can display fixture data and diagnostics, but it cannot accept evidence, promote candidates, mutate indexes, or call connectors.

The WinForms proof follows this model by loading caller-supplied local fixture text or an embedded fallback fixture and rendering read-only panels.
