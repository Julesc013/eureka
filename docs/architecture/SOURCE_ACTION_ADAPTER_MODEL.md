# Source Action Adapter Model

Adapters implement the generic source action interface. They provide manifests, supported action kinds, fixture/mock transports, and normalizers. Source-specific adapters must not own review acceptance, promotion, store mutation, downloads, extraction, deployment, or public fanout.
