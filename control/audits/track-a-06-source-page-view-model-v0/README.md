# TRACK-A-06 SourcePage View Model v0

Track A-06 adds the first canonical SourcePage view model contract for Eureka.
It defines the public meaning layer that standard, lite, HTML 3.2-ish, text,
file-tree summary, API-adjacent, manifest, snapshot, relay, terminal, print,
and native-card projections must preserve before renderer or runtime refactors
widen.

## What Was Added

- SourcePage view model schema.
- Reference documentation for source identity, policy/access posture,
  connector-disabled status, source cache and evidence ledger posture, coverage
  gaps, rights/risk/privacy posture, actions, blocked actions, and
  representation hints.
- Publication policy inventory for SourcePageView.
- Four compact public-safe examples for minimal, recorded fixture, placeholder,
  and source-gap pages.
- Stdlib-only validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why This Comes Before Renderer And Runtime Refactors

Renderer or runtime work needs one canonical SourcePage meaning before it can
project that meaning into standard HTML, lite HTML, old-client HTML, text,
file-tree summaries, API-adjacent examples, future snapshots, future relay,
future terminal, print, or future native-card views. This contract makes source
posture explicit without activating source-page runtime behavior, source sync,
connectors, live probes, or hosted source behavior.

## Track A Support

TRACK-A-01 defined host/profile/representation selection. TRACK-A-02 defined
semantic renderer parity. TRACK-A-03 bound `source_detail` to `SourcePageView`.
TRACK-A-04 defined `SearchPageView`. TRACK-A-05 defined `ObjectPageView`.
TRACK-A-06 now defines the field-level SourcePageView meaning that later
renderer and runtime work must preserve.

## Projection Protection

The contract requires renderers to preserve canonical source identity, source
type and authority posture, source policy gates, access posture, coverage
depth, connector mode and disabled live/source-sync status, source cache and
evidence ledger truth boundaries, rights/risk/privacy posture, allowed and
blocked actions, candidate/review state, limitations, and gaps. Plain text,
lite, file-tree, manifest, snapshot, relay, terminal, print, and native-card
projections may simplify presentation only.

## Relationship To Source And Evidence Governance

SourcePageView references existing source registry, source pack, evidence pack,
source cache, and evidence ledger governance as inputs, not as permission to
mutate or execute them:

- `contracts/source_registry/`
- `docs/reference/SOURCE_PACK_CONTRACT.md`
- `docs/reference/EVIDENCE_PACK_CONTRACT.md`
- `docs/reference/SOURCE_CACHE_CONTRACT.md`
- `docs/reference/EVIDENCE_LEDGER_CONTRACT.md`

Future source pages may connect to source/evidence records after governed
runtime work. This milestone does not create source connectors, source sync
workers, source cache writes, evidence ledger writes, public index changes, or
source-page routes.

## Source Gaps

Source gap examples demonstrate that known gaps are first-class public-safe
output. Manual observation placeholders, coverage gaps, policy review gaps, and
evidence ledger gaps stay visible and must not be represented as completed
external baselines or accepted truth.

## Deferred

- NeedPage and CandidatePage view model contracts for TRACK-A-07.
- Runtime renderer implementation.
- Source-page route activation.
- Source sync and source connector runtime.
- Hosted backend/public alpha, which remains Track E/operator-gated.
- Live probes, downloads, uploads, accounts, telemetry, native projects, relay
  runtime, snapshot runtime, generated site artifacts, rights clearance,
  malware safety, authorized bulk access, and master-index mutation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/source_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-06-source-page-view-model-v0/track_a_06_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
- `python scripts/validate_source_page_view_model.py`
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
- No source-page runtime behavior.
- No live probes, source connectors, or source sync runtime.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No master-index mutation.
- No native project creation.
- No rights-clearance claims.
- No malware-safety claims.
- No authorized-bulk-access claims.
- No broad crawling or scraping claims.
- No broad docs rewrite.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-07 - NeedPage and CandidatePage view model contracts.
