# TRACK-A-11 Projection Gap Report

## Current Aligned Artifacts

- `site/dist/search.html`, `site/dist/lite/search.html`,
  `site/dist/text/search.txt`, `site/dist/files/search.README.txt`, and
  `site/dist/data/search_handoff.json` are present.
- The audited artifacts preserve static handoff, hosted-unavailable,
  local/prototype `local_index_only`, and disabled live-probe/download/upload/
  account/telemetry posture.
- `search_handoff.json` structurally records disabled capability booleans and
  a no-hosted-search claim.

## Missing Or Unknown Semantic Mappings

- Current artifacts are not generated from or traced to a canonical
  `SearchPageView` fixture.
- No artifact embeds a canonical `view_model_id`.
- Text and file-tree note artifacts do not machine-verify source/evidence
  posture as strongly as the HTML and JSON artifacts.
- Existing handoff profile labels such as `standard_web` and `api_client` need
  explicit mapping to Track A representation profiles.

## Artifact-Specific Gaps

- `site/dist/search.html`: aligned as a static handoff, but not fixture-traced.
- `site/dist/lite/search.html`: aligned as no-JS lite HTML, but not
  fixture-traced.
- `site/dist/text/search.txt`: aligned on safety posture, with source/evidence
  posture not machine-verified.
- `site/dist/files/search.README.txt`: aligned on safety posture, with
  source/evidence posture not machine-verified.
- `site/dist/data/search_handoff.json`: strongest structural safety posture,
  but uses legacy profile labels that need Track A mapping.

## Recommended Next Refactor

`TRACK-A-12 - Static SearchPage projection fixture and generator plan` should
create a canonical static-handoff `SearchPageView` fixture, generate all static
representations from it, compare generated output to current artifacts, and
preserve route identity and no-JS/static behavior.

## Risks

- This audit uses conservative substring and JSON-field checks, not full HTML
  renderer parity.
- WARN status is expected until a canonical fixture and projection generator
  exist.

## No-Goals Preserved

No `site/dist` files were changed or regenerated. No hosted search, live probes,
downloads, uploads, accounts, telemetry, native runtime, or master-index
mutation were enabled.
