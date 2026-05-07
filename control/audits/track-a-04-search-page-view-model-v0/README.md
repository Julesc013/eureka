# TRACK-A-04 SearchPage View Model v0

Track A-04 adds the first canonical SearchPage view model contract for Eureka.
It defines the public meaning layer that standard, lite, HTML 3.2-ish, text,
file-tree summary, API-adjacent, snapshot, relay, terminal, and native-card
projections must preserve before renderer or runtime refactors widen.

## What Was Added

- SearchPage view model schema.
- Reference documentation for SearchPageView identity, posture, results,
  absence, controls/actions, and representation hints.
- Publication policy inventory for SearchPageView.
- Four compact public-safe examples for initial, minimal, absence, and result
  card-backed search pages.
- Stdlib-only validator and unittest coverage.
- Task-local audit and AIDE evidence.
- Narrow AIDE commit-message tooling alignment so the task-required
  `contracts(...)` commit subject type passes local checks.

## Why This Comes Before Renderer And Runtime Refactors

Renderer or runtime work needs one canonical SearchPage meaning before it can
project that meaning into standard HTML, lite HTML, old-client HTML, text,
file-tree summaries, API-adjacent examples, future snapshots, future relay,
future terminal, or future native-card views. This contract makes the view model
explicit without changing current local/static search behavior.

## Track A Support

TRACK-A-01 defined host/profile/representation selection. TRACK-A-02 defined
semantic renderer parity. TRACK-A-03 bound the search route family to
`SearchPageView`. TRACK-A-04 now defines the field-level SearchPageView meaning
that later renderer work must preserve.

## Projection Protection

The contract requires renderers to preserve query identity, source/evidence
posture, result state, candidate/provisional state, rights/risk posture,
allowed and blocked actions, limitations, gaps, absence scope, canonical route,
and stable result IDs. Plain text, lite, file-tree, snapshot, relay, terminal,
and native-card projections may simplify presentation only.

## Relation To Search API And Result Card Contracts

SearchPageView references the existing public search API and result-card
contracts:

- `contracts/api/search_response.v0.json`
- `contracts/api/search_result_card.v0.json`

It may carry result-card references or compact result-card-shaped examples, but
it does not duplicate or change those contracts.

## Deferred

- ObjectPage view model contract for TRACK-A-05.
- Runtime renderer implementation.
- Hosted backend/public alpha, which remains Track E/operator-gated.
- Live probes, source connectors, downloads, uploads, accounts, telemetry,
  native projects, relay runtime, snapshot runtime, generated site artifacts,
  and master-index mutation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/search_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-04-search-page-view-model-v0/track_a_04_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval list`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py adapter validate`

See `validation.md` for observed results.

## No-Goals

- No Eureka product runtime changes.
- No hosted backend claim.
- No deployment, DNS, CNAME, or custom-domain changes.
- No public route activation.
- No live probes or source connectors.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No master-index mutation.
- No native project creation.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-05 - ObjectPage view model contract.
