# AIDE Latest Task Packet

## PHASE

H9-BUNDLE-02 - Media, music, image, video, and map fixture runtimes and normalizers. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Add committed-fixture-only H9 media metadata normalizers and replay outputs after H9-BUNDLE-01 established policy-pack-only governance.

## WHY

H9-BUNDLE-01 added source records, policy packs, identity/relation/fingerprint/rights/safety policies, coverage and scorecard previews, and no-live/no-download/no-upload boundaries for media metadata sources. H9-BUNDLE-02 can now prove parsing and boundary behavior with synthetic or repo-local fixtures.

## CONTEXT_REFS

- `control/audits/h9-bundle-01-media-metadata-policy-packs-v0/`
- `control/inventory/source_packs/h9_media_metadata_sources.json`
- `control/inventory/source_packs/h9_media_metadata_source_pack_policy.json`
- `control/inventory/source_packs/h9_media_metadata_no_live_call_policy.json`
- `control/inventory/source_packs/h9_media_metadata_no_download_upload_policy.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `AGENTS.md`

## ALLOWED_PATHS

- H9 fixture contracts, committed fixtures, normalizer runtime modules, replay outputs, examples, docs, scripts, tests, audit pack, and AIDE routing metadata only.
- `.aide/queue/`, `.aide/context/`, and `.aide/reports/` routing metadata updates for the H9 fixture-runtime handoff.

## FORBIDDEN_PATHS

- site distribution output root
- public index data root
- runtime/**
- contracts/**
- surfaces/**
- site/**
- native/**
- crates/**
- connectors/**
- packaging/**
- third_party/**
- master-index or publication roots
- media download/upload, fingerprint cache, image/video/audio/map cache, restricted-source, OCR/full-text, and local private-state roots
- product runtime behavior outside explicit future H9 fixture-runtime scope

## IMPLEMENTATION

- Read H9-BUNDLE-01 audit output and media metadata policy packs first.
- Add committed fixture-only normalizers for H9 sources.
- Convert public-safe fixtures into normalized media metadata records and candidate/previews only.
- Do not enable live probes, source sync, downloads, uploads, fingerprint generation/submission, scraping, crawling, bypass, or truth acceptance.

## VALIDATION

- Run `git status --short`.
- Run `git diff --check`.
- Run the H9 fixture-runtime validator added by the task.
- Run relevant H9/H8/H7/core validators if present.
- Run focused unit tests and `python scripts/check_architecture_boundaries.py` when runtime or connector boundaries are touched.
- Run AIDE Lite checks where practical.
- Run `.aide/scripts/aide_lite.py doctor`.
- Run `.aide/scripts/aide_lite.py validate`.
- Run `.aide/scripts/aide_lite.py test`.
- Run `.aide/scripts/aide_lite.py selftest`.
- Run `.aide/scripts/aide_lite.py eval run`.
- Run `.aide/scripts/aide_lite.py verify`.

## EVIDENCE

- `control/audits/h9-bundle-01-media-metadata-policy-packs-v0/`
- `.aide/queue/H9-BUNDLE-02/task.yaml`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`

## ACCEPTANCE

- H9 fixture runtime remains committed-fixture-only.
- Media/music/image/video/map/fingerprint/rights/safety normalized outputs remain candidates or previews.
- No public/master index mutation or product behavior change occurs.
- No source, evidence, candidate, media, music, image/video/map, fingerprint, rights, safety, or public truth is accepted.

## NON_GOALS

- No live calls, downloads, uploads, fingerprint generation/submission, scraping, crawling, source sync, public/master index mutation, source/evidence/candidate truth acceptance, or product behavior changes.
- Proceed without changing Eureka product behavior.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1500
