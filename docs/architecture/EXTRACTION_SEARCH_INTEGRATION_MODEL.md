# Extraction Search Integration Model

F-BUNDLE-02 routes F-BUNDLE-01 fixture extraction results into local previews:

- extraction result -> candidate effects
- candidate effects -> source-cache/evidence previews and review seeds
- members/manifests/blocked results -> search gaps
- members/manifests/blocked results -> future WorkUnit seeds
- integration summaries -> Track G readiness

The model is intentionally non-mutating. Public search, public index, master index, candidate store, evidence ledger, and review queue remain unchanged.
