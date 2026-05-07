# TRACK-A-09 Remaining Risks

- AIDE Lite verifier remains WARN-only because the compact task packet has
  generic scope metadata that does not enumerate the A09 paths, and the latest
  review packet references optional AIDE status artifacts that are absent in
  this checkout.
- EvidencePageView and ComparePageView intentionally use inherited semantic
  parity policies from the route matrix until a later slice decides whether
  dedicated parity policies are needed.
- The new contracts are governance and validation artifacts only. Renderer
  implementation, runtime wiring, downloads, evidence ledger workflows, scoped
  absence runtime, comparison runtime, native handoff, relay, snapshot, and
  hosted public alpha remain deferred.
