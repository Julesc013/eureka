# TRACK-A-05 ObjectPage View Model v0

Track A-05 adds the first canonical ObjectPage view model contract for Eureka.
It defines the public meaning layer that standard, lite, HTML 3.2-ish, text,
file-tree summary, API-adjacent, snapshot, relay, terminal, print, and
native-card projections must preserve before renderer or runtime refactors
widen.

## What Was Added

- ObjectPage view model schema.
- Reference documentation for object identity, state/version posture,
  representation/member summaries, source/evidence/provenance posture,
  compatibility, rights, risk, actions, gaps, and representation hints.
- Publication policy inventory for ObjectPageView.
- Four compact public-safe examples for minimal, software-like, member, and
  candidate object pages.
- Stdlib-only validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why This Comes Before Renderer And Runtime Refactors

Renderer or runtime work needs one canonical ObjectPage meaning before it can
project that meaning into standard HTML, lite HTML, old-client HTML, text,
file-tree summaries, API-adjacent examples, future snapshots, future relay,
future terminal, print, or future native-card views. This contract makes the
view model explicit without activating object-page runtime behavior.

## Track A Support

TRACK-A-01 defined host/profile/representation selection. TRACK-A-02 defined
semantic renderer parity. TRACK-A-03 bound `object_page_future` to
`ObjectPageView`. TRACK-A-04 defined `SearchPageView`. TRACK-A-05 now defines
the field-level ObjectPageView meaning that later renderer and runtime work
must preserve.

## Projection Protection

The contract requires renderers to preserve canonical object identity, object
state/version unknowns, source/evidence posture, representation and member
posture, parent lineage, provenance, compatibility, rights/risk posture,
allowed and blocked actions, candidate/review state, limitations, and unresolved
gaps. Plain text, lite, file-tree, manifest, snapshot, relay, terminal, print,
and native-card projections may simplify presentation only.

## Relationship To Result Cards And Source/Evidence Records

ObjectPageView references the public search result-card contract and existing
object page contract as inputs, not as permission to mutate public search or
activate object pages:

- `contracts/api/search_result_card.v0.json`
- `contracts/views/search_page.v0.json`
- `contracts/pages/object_page.v0.json`

Future object pages may connect to source/evidence records after governed
runtime work. This milestone does not create source/evidence runtime outputs,
candidate promotion, public index changes, or object-page routes.

## Smallest Actionable Unit

Member object examples demonstrate the smallest-actionable-unit doctrine: a
useful member inside a container may be the object page target, but parent
container lineage, source, evidence, and representation context must remain
visible.

## Deferred

- SourcePage view model contract for TRACK-A-06.
- Runtime renderer implementation.
- Object-page route activation.
- Hosted backend/public alpha, which remains Track E/operator-gated.
- Live probes, source connectors, downloads, uploads, accounts, telemetry,
  native projects, relay runtime, snapshot runtime, generated site artifacts,
  rights clearance, malware safety, verified installability, and master-index
  mutation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/object_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-05-object-page-view-model-v0/track_a_05_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
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
- No object-page runtime behavior.
- No live probes or source connectors.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No master-index mutation.
- No native project creation.
- No rights-clearance claims.
- No malware-safety claims.
- No verified-installability claims.
- No broad docs rewrite.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-06 - SourcePage view model contract.
