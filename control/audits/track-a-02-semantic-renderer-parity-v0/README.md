# TRACK-A-02 Semantic Renderer Parity v0

Track A-02 adds the semantic renderer parity contract for Eureka. It defines
what every renderer or projection must preserve when standard HTML, lite HTML,
HTML 3.2-ish, text, file-tree, API JSON, manifest JSON, future snapshot,
future relay, future terminal, future native-card, and print surfaces present
the same public-safe meaning.

## What Was Added

- Semantic renderer parity schema.
- Reference documentation for semantic parity requirements and no-goals.
- Publication inventory with parity policies for required route/view families.
- Compact public-safe examples for search card, object page, and absence page
  parity.
- Stdlib-only validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why This Comes Before Renderer Work

Renderer/runtime work can easily drift into accidental product semantics:
hiding uncertainty, softening blocked actions, implying hosted/live behavior, or
treating constrained projections as disposable fallbacks. This contract pins the
semantic obligations first so future view-model and renderer code can be tested
against one canonical meaning instead of rediscovering it per surface.

## Track A Support

Track A needs one resolver truth, one route meaning, one canonical view model,
and many compatible projections. TRACK-A-01 established host and representation
selection. TRACK-A-02 adds the parity rules those profiles must obey.

## Projection Protection

Lite, text, file-tree, snapshot, relay, terminal, print, and future native-card
surfaces may simplify layout, media, interaction, and density. They must still
preserve identity, source posture, evidence posture, compatibility caveats,
rights/risk posture, allowed actions, blocked actions, limitations, gaps,
absence scope, candidate/review state, canonical links, and stable IDs.

## Deferred

- Runtime renderers and canonical view-model implementation.
- Route/view/representation matrix details for TRACK-A-03.
- Hosted backend, DNS/custom domains, live probes, source connectors, native
  projects, relay runtime, snapshot runtime, downloads, uploads, accounts,
  telemetry, execution, and master-index mutation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/semantic_renderer_parity_policy.json`
- `python -m json.tool control/audits/track-a-02-semantic-renderer-parity-v0/track_a_02_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
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
- No public search result-card runtime semantic change.

## Next Task Recommendation

TRACK-A-03 - Route/view/representation matrix.
