# TRACK-A-08 PackPage TaskPage And ReviewPage View Models v0

Track A-08 adds the first canonical PackPage, TaskPage, and ReviewPage view
model contracts for Eureka. The bundle defines public meaning for portable
packs, future work units, and review/promotion records before renderer or
runtime refactors widen.

## What Was Added

- PackPage, TaskPage, and ReviewPage view model schemas.
- Reference documentation for pack validation/import-disabled posture, task
  execution-disabled posture, review decisions, promotion requirements,
  rights/risk/privacy, actions, blocked actions, and representation hints.
- Publication policy inventories for PackPageView, TaskPageView, and
  ReviewPageView.
- Four compact PackPage examples.
- Four compact TaskPage examples.
- Four compact ReviewPage examples.
- Stdlib-only combined validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why These Come Before Renderer And Runtime Refactors

Packs, tasks, and reviews are high-risk truth-boundary surfaces. A renderer
that makes a pack look imported, a task look executable, or a review look like
accepted promotion can corrupt public meaning without touching runtime code.
Track A-08 establishes the view-model contract before renderers or runtime
handoffs can blur those states.

## Track A Support

TRACK-A-01 through TRACK-A-07 established representation selection, semantic
parity, route/view bindings, SearchPageView, ObjectPageView, SourcePageView,
NeedPageView, and CandidatePageView. TRACK-A-08 extends that spine to packs,
work units, and review governance.

## Packs, Work Units, Nodes, Review Queues, And Master-Index Governance

PackPageView supports source, evidence, index, contribution, review, and future
snapshot-style pack summaries as portable validate-only records. It keeps
import, upload, moderation, automatic acceptance, public search impact, and
master-index mutation disabled.

TaskPageView supports future work-unit and node-task handoff pages as bounded
requests for governed work. It keeps node runtime, autonomous execution, live
source access, model/provider calls, downloads, public submissions, and
master-index mutation disabled.

ReviewPageView supports queue entries, validation posture, review decisions,
deferrals, rejections, conflicts, and promotion requirements. It keeps hosted
moderation, account-backed review, write routes, public submission runtime,
accepted public status, and master-index mutation disabled.

## Public Truth Protection

The bundle forbids converting pack contents, work-unit outputs, review records,
candidates, source observations, evidence candidates, contribution items,
demand signals, or AI drafts into accepted public truth. It also keeps rights
clearance, malware safety, verified installability, safe execution, authorized
bulk access, public acceptance, hosted moderation, active submission runtime,
and production suitability out of current examples.

## Projection Protection

Standard, lite, old-client HTML, text, file-tree, API-adjacent, manifest,
snapshot, relay, terminal, print, and native-card projections may simplify
presentation only. They must preserve identity, status, validation posture,
review gates, promotion requirements, provenance, rights/risk/privacy caveats,
limitations, gaps, and blocked actions.

## Deferred

- DownloadManifest, EvidencePage, AbsencePage, and ComparePage view model
  contracts for TRACK-A-09.
- Runtime renderer implementation.
- Pack import, hosted upload/submission, review/moderation runtime, node
  runtime, autonomous execution, model/provider calls, source sync, source
  connectors, and master-index mutation.
- Hosted backend/public alpha, which remains Track E/operator-gated.
- Live probes, downloads, uploads, accounts, telemetry, native projects, relay
  runtime, snapshot runtime, generated site artifacts, rights clearance,
  malware safety, verified installability, public acceptance, and production
  suitability.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/pack_page_view_model_policy.json`
- `python -m json.tool control/inventory/publication/task_page_view_model_policy.json`
- `python -m json.tool control/inventory/publication/review_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-08-pack-task-review-page-view-models-v0/track_a_08_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
- `python scripts/validate_source_page_view_model.py`
- `python scripts/validate_need_candidate_page_view_models.py`
- `python scripts/validate_pack_task_review_page_view_models.py`
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
- No pack import, node, review, moderation, hosted upload, or submission
  runtime.
- No live probes, source connectors, or source sync runtime.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No raw query telemetry claims.
- No master-index mutation.
- No native project creation.
- No rights-clearance, malware-safety, verified-installability, safe-execution,
  authorized-bulk-access, production-suitability, or public-truth claims.
- No broad docs rewrite.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-09 - DownloadManifest, EvidencePage, AbsencePage, and ComparePage view
model contracts.
