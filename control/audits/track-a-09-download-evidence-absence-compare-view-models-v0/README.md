# TRACK-A-09 Download Evidence Absence Compare View Models v0

Track A-09 adds the first canonical DownloadManifest, EvidencePage,
AbsencePage, and ComparePage view model contracts for Eureka. The bundle
defines public meaning for acquisition manifests, evidence records, absence
reports, and comparison pages before renderer or runtime refactors widen.

## What Was Added

- DownloadManifestView, EvidencePageView, AbsencePageView, and ComparePageView
  schemas.
- Reference documentation for manifest, evidence, absence, and comparison
  truth boundaries.
- Publication policy inventories for all four view families.
- Three compact DownloadManifest examples.
- Four compact EvidencePage examples.
- Four compact AbsencePage examples.
- Four compact ComparePage examples.
- Stdlib-only combined validator and unittest coverage.
- Task-local audit and AIDE evidence.

## Why These Come Before Renderer And Runtime Refactors

These surfaces are easy places to overclaim. A manifest can look like a
downloader, evidence can look like truth, absence can look omniscient, and a
comparison can look like a merge decision. Track A-09 fixes the meaning layer
first so later renderers can simplify presentation without changing posture.

## Track A Support

TRACK-A-01 through TRACK-A-08 established representation selection, semantic
parity, route/view bindings, and canonical view models for search, objects,
sources, needs, candidates, packs, tasks, and reviews. TRACK-A-09 completes the
remaining Track A page-family contracts needed before the policy index and
cross-contract validator in TRACK-A-10.

## Projection Protection

Standard, lite, old-client HTML, text, file-tree, API-adjacent, manifest,
snapshot, relay, terminal, print, and native-card projections may simplify
presentation only. They must preserve identity, source/evidence/provenance
posture, rights/risk/privacy posture, limitations, gaps, conflict state, and
blocked actions.

## Truth And Runtime Protection

- DownloadManifestView is manifest metadata, not a downloader.
- EvidencePageView exposes claims and observations without accepting them as
  truth.
- AbsencePageView preserves searched scope and never claims exhaustive global
  search.
- ComparePageView preserves disagreement and never merges, deduplicates,
  promotes, or mutates records.

## Deferred

- View-model policy index and cross-contract validator for TRACK-A-10.
- Runtime renderer implementation.
- Downloads, installers, execution, package-manager handoff, relay/native
  handoff runtime, live probes, source sync, source connectors, pack import,
  review runtime, node runtime, uploads, accounts, telemetry, and master-index
  mutation.
- Hosted backend/public alpha, which remains Track E/operator-gated.
- Generated site artifacts and native project creation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/download_manifest_view_model_policy.json`
- `python -m json.tool control/inventory/publication/evidence_page_view_model_policy.json`
- `python -m json.tool control/inventory/publication/absence_page_view_model_policy.json`
- `python -m json.tool control/inventory/publication/compare_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-09-download-evidence-absence-compare-view-models-v0/track_a_09_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
- `python scripts/validate_source_page_view_model.py`
- `python scripts/validate_need_candidate_page_view_models.py`
- `python scripts/validate_pack_task_review_page_view_models.py`
- `python scripts/validate_download_evidence_absence_compare_view_models.py`
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
- No live probes, source connectors, source sync runtime, node runtime,
  autonomous runtime, pack import runtime, hosted upload/submission runtime, or
  review/moderation runtime.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No raw query telemetry claims.
- No master-index mutation.
- No native project creation.
- No rights-clearance, malware-safety, verified-installability, safe-execution,
  evidence-truth, exhaustive-global-search, automatic-merge, deduplication, or
  promotion claims.
- No broad docs rewrite.
- No generated site artifact mutation.
- No public search route/runtime semantic change.

## Next Task Recommendation

TRACK-A-10 - View model policy index and cross-contract validator.
