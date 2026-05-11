# AIDE Latest Task Packet

## PHASE

H9-BUNDLE-03 - Media, music, image, video, and map approved metadata-only live probes. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Add approval-gated bounded metadata-only live-probe framework for H9 media metadata sources after H9-BUNDLE-02 fixture runtime passed.

## WHY

H9-BUNDLE-02 added committed-fixture-only normalizers, replay outputs, candidates, source-cache/evidence previews, tests, and audit evidence for 20 H9 media metadata sources. H9-BUNDLE-03 may now define fail-closed live-probe envelopes without approving broad access or media payload handling.

## CONTEXT_REFS

- `control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/`
- `control/audits/h9-bundle-01-media-metadata-policy-packs-v0/`
- `runtime/connectors/h9_media_metadata/`
- `examples/connectors/h9_media_metadata/fixtures/`
- `examples/connectors/h9_media_metadata/normalized/`
- `examples/connectors/h9_media_metadata/replay_results/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `AGENTS.md`

## ALLOWED_PATHS

- H9 live-probe contracts, policies, source-specific metadata wrappers, examples, docs, scripts, tests, audit pack, and AIDE routing metadata only.
- `.aide/queue/`, `.aide/context/`, and `.aide/reports/` routing metadata updates for the H9 live-probe handoff.

## FORBIDDEN_PATHS

- site distribution output root
- public index data root
- master-index or publication roots
- media download/upload, fingerprint cache, image/video/audio/map cache, restricted-source, OCR/full-text, and local private-state roots
- product runtime behavior outside explicit future H9 live-probe scope

## IMPLEMENTATION

- Read H9-BUNDLE-02 audit output and fixture runtime artifacts first.
- Default behavior must remain offline preflight and fail-closed.
- Do not enable broad media search, source sync, media downloads/uploads, fingerprint generation/submission, scraping, crawling, bypass, public/master index mutation, or truth acceptance.

## VALIDATION

- Run `git status --short`.
- Run `git diff --check`.
- Run the H9 live-probe validator added by the task.
- Run relevant H9/H8/H7/core validators if present.
- Run focused unit tests and `python scripts/check_architecture_boundaries.py` when runtime or connector boundaries are touched.
- Run AIDE Lite checks where practical.

## EVIDENCE

- `control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/`
- `.aide/queue/H9-BUNDLE-03/task.yaml`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`

## ACCEPTANCE

- H9 live probes remain metadata-only, approval-gated, and fail-closed by default.
- No media payload handling, upload, fingerprinting, scraping, crawling, restricted access, source sync, public/master index mutation, or truth acceptance occurs.

## NON_GOALS

- No live calls by default, downloads, uploads, fingerprint generation/submission, scraping, crawling, source sync, public/master index mutation, source/evidence/candidate truth acceptance, or product behavior changes.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1500
