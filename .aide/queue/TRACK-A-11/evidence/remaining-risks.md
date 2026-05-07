# TRACK-A-11 Remaining Risks

- Existing static SearchPage artifacts are not yet generated from or traced to
  a canonical `SearchPageView` fixture.
- The audit uses conservative substring and JSON-field checks, not full HTML
  renderer parity.
- `search_handoff.json` contains legacy profile labels such as `standard_web`
  and `api_client`; these need explicit Track A mapping in the next refactor.
- AIDE Lite `verify` and `review-pack` remain WARN-only because the compact
  task scope metadata does not exactly enumerate the new A11 paths and the
  latest review packet references optional AIDE status artifacts that are not
  present.
