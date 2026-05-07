# TRACK-A-03 Route/View/Representation Matrix v0

Track A-03 adds the route/view/representation matrix for Eureka. It binds
canonical route families to canonical view-model families, allowed
representation profiles, host-profile exposure defaults, semantic parity
policies, current status, and deferred behavior.

## What Was Added

- Route/view/representation matrix schema.
- Reference documentation for route identity, status vocabulary, host/profile
  binding, semantic parity binding, and public-alpha gating.
- Publication inventory with 25 route families and 25 canonical view families.
- Compact public-safe example matrix.
- Stdlib-only validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why This Comes Before View-Model Contracts

View-model contracts need one route meaning and one canonical view-family
assignment before field-level view models are specified. This matrix prevents
future SearchPage, ObjectPage, SourcePage, snapshot, relay, and native-card
contracts from choosing route identity, host exposure, or representation
semantics independently.

## Track A Support

TRACK-A-01 established host/profile/representation selection. TRACK-A-02
established semantic renderer parity. TRACK-A-03 connects those contracts to
canonical route and view families so Track A can proceed to concrete view-model
contracts without route identity drift.

## Route Identity Drift Guard

The matrix forbids route splits such as `/modern/search`, `/old/search`,
`/mobile/search`, `/retro/search`, `/desktop/search`, `/legacy/object`, and
`/classic/object`. Host, format, profile, and capability negotiation select a
projection; they do not create a different route meaning.

## Hosted Alpha Gate

Early public-alpha-shaped work remains local, static, staging, or localhost
rehearsal evidence. Actual hosted public alpha remains Track E and
operator-gated. The matrix does not imply that dynamic hosted search is active.

## Deferred

- Field-level SearchPage view model contract for TRACK-A-04.
- Route-specific semantic parity policies for inherited bindings where useful.
- Runtime renderer implementation.
- Hosted backend, DNS/custom domains, live probes, source connectors, native
  projects, relay runtime, snapshot runtime, downloads, uploads, accounts,
  telemetry, execution, and master-index mutation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/route_view_representation_matrix.json`
- `python -m json.tool control/audits/track-a-03-route-view-representation-matrix-v0/track_a_03_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
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
- No broad docs rewrite.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-04 - SearchPage view model contract.
