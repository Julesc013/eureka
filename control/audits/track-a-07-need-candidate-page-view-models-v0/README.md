# TRACK-A-07 NeedPage And CandidatePage View Models v0

Track A-07 adds the first canonical NeedPage and CandidatePage view model
contracts for Eureka. The bundle defines public meaning for unresolved needs,
known absence, source gaps, candidate leads, provisional discoveries, and review
state before renderer or runtime refactors widen.

## What Was Added

- NeedPage and CandidatePage view model schemas.
- Reference documentation for unresolved demand, scoped absence, source gaps,
  provisional candidates, evidence posture, review state, rights/risk/privacy,
  actions, blocked actions, and representation hints.
- Publication policy inventories for NeedPageView and CandidatePageView.
- Four compact NeedPage examples.
- Four compact CandidatePage examples.
- Stdlib-only combined validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why These Come Before Renderer And Runtime Refactors

Need and candidate pages are where public truth can get polluted most easily:
weak demand can look like proof, absence can look global, and provisional
discoveries can look accepted. Track A-07 creates the view-model contract before
any renderer, node, review, source, or runtime work can accidentally blur those
states.

## Track A Support

TRACK-A-01 through TRACK-A-06 established representation selection, semantic
parity, route/view bindings, SearchPageView, ObjectPageView, and SourcePageView.
TRACK-A-07 extends that spine to unresolved needs and candidate review surfaces.

## Known Absence, Demand, Work Units, Candidates, Packs, And Review

NeedPageView supports scoped known absence, aggregate-only demand posture,
source gaps, near misses, candidates, and future work-unit/contribution refs
without enabling telemetry, account watches, probe queues, node tasks, or public
submissions.

CandidatePageView supports provisional findings from needs, sources, source
cache records, evidence packs, contribution packs, index packs, manual
observations, future extraction, future node work, discussions, and future AI
drafts without accepting them as public truth.

## Public Truth Protection

The bundle forbids converting demand signals, source observations, evidence
candidates, contribution items, discussion comments, or AI drafts into accepted
truth. It also keeps rights clearance, malware safety, installability, safe
execution, public acceptance, exhaustive global search, master-index mutation,
and hosted/live/source-sync claims out of current examples.

## Projection Protection

Standard, lite, old-client HTML, text, file-tree, API-adjacent, manifest,
snapshot, relay, terminal, print, and native-card projections may simplify
presentation only. They must preserve identity, scope, demand privacy, absence,
candidate status, evidence posture, review requirements, conflicts, rights/risk
caveats, limitations, gaps, and blocked actions.

## Deferred

- PackPage, TaskPage, and ReviewPage view model contracts for TRACK-A-08.
- Runtime renderer implementation.
- Need or candidate route activation.
- Node task runtime, public submissions, review runtime, candidate promotion,
  source sync, source connectors, and master-index mutation.
- Hosted backend/public alpha, which remains Track E/operator-gated.
- Live probes, downloads, uploads, accounts, telemetry, native projects, relay
  runtime, snapshot runtime, generated site artifacts, rights clearance,
  malware safety, verified installability, public acceptance, and exhaustive
  global search.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/need_page_view_model_policy.json`
- `python -m json.tool control/inventory/publication/candidate_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-07-need-candidate-page-view-models-v0/track_a_07_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
- `python scripts/validate_source_page_view_model.py`
- `python scripts/validate_need_candidate_page_view_models.py`
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
- No need or candidate runtime behavior.
- No live probes, source connectors, or source sync runtime.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No raw query telemetry claims.
- No master-index mutation.
- No native project creation.
- No rights-clearance, malware-safety, or verified-installability claims.
- No accepted-public-truth claims from candidates.
- No exhaustive-global-search claims.
- No broad docs rewrite.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-08 - PackPage, TaskPage, and ReviewPage view model contracts.
