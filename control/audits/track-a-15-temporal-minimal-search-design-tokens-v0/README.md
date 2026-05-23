# TRACK-A-15 Temporal Minimal Search Design Tokens

TRACK-A-15 adds contract-only UI design-token governance for Eureka's future
search-like public surfaces.

## What Was Added

- Generic design-token contract and Temporal Minimal Search design-language
  contract under `contracts/surface/ui/`.
- Design-token policy, concrete Temporal Minimal Search token inventory, and
  design profile matrix under `control/inventory/publication/`.
- Compact public-safe examples for minimal, default, high-contrast, and
  text-only profiles.
- Reference and operations documentation.
- Stdlib-only validators and contract tests.

## Why After Projection Audits

TRACK-A-11 through TRACK-A-14 recorded how current static/demo artifacts relate
to canonical view-model meaning. Design tokens come next so future renderer work
has a governed presentation language before any CSS, template, or static-site
refactor begins.

## Renderer Support

Temporal Minimal Search supports standard HTML, lite HTML, HTML 3.2-ish, text,
file-tree, API-adjacent JSON, future snapshot, future relay, future terminal,
future native-card, print, and high-contrast projections as profiles over the
same semantics.

## Branding And Trade Dress

The contract allows neutral classic search grammar: sparse layout, blue links,
source/status lines, compact metadata, and GET forms. It forbids copied logos,
exact third-party page identity, exact third-party CSS/HTML, affiliation
claims, deceptive source labels, and misleading official labels.

## Old Clients

Old-client, text-only, file-tree, print, and high-contrast projections are
first-class. They may lose polish, but they must preserve source, evidence,
status, rights, risk, limitations, gaps, absence scope, and blocked actions.

## Validation Commands

```text
python -m json.tool control/inventory/publication/design_token_policy.json
python -m json.tool control/inventory/publication/temporal_minimal_search_tokens.json
python -m json.tool control/inventory/publication/design_profile_matrix.json
python -m json.tool control/audits/track-a-15-temporal-minimal-search-design-tokens-v0/track_a_15_report.json
python scripts/validate_design_tokens.py
python scripts/validate_temporal_minimal_search.py
python scripts/validate_track_a_contracts.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## No-Goals

No CSS, renderer, frontend framework, public route, hosted backend, live source,
download, upload, account, telemetry, native runtime, or generated site artifact
was added or changed.

## Next Task

TRACK-A-16 - Renderer parity harness
