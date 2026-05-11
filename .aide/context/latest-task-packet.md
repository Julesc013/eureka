# AIDE Latest Task Packet

## PHASE

H9-BUNDLE-04 - Media, music, image, video, and map review integration and quality delta. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Integrate H9 fixture-equivalent and blocked live-probe outputs into review seeds, quality delta, connector scorecards, postmortem, and H9 exit evidence.

## WHY

H9-BUNDLE-03 added fail-closed metadata-only live-probe policies, wrappers, scripts, examples, tests, and blocked audit evidence without external calls or media payload handling.

## CONTEXT_REFS

- `control/audits/h9-bundle-03-media-metadata-live-probes-v0/`
- `control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/`
- `examples/connectors/h9_media_metadata/live_probe_results/`
- `examples/connectors/h9_media_metadata/live_probe_outputs/`
- `runtime/connectors/h9_media_metadata/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/memory/project-state.md`
- `AGENTS.md`

## ALLOWED_PATHS

H9 review integration artifacts requested by the next task, plus `.aide/` routing and operating metadata only. Keep edits narrowly scoped and do the work without changing Eureka product behavior.

## FORBIDDEN_PATHS

- `runtime/**` outside the explicit H9 review-integration scope
- `contracts/**` outside the explicit H9 review-integration scope
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- site distribution output root
- public index data root
- master-index or publication roots
- media download/upload/fingerprint/restricted-source roots
- product behavior surfaces

## IMPLEMENTATION

Use H9-BUNDLE-02 fixture replay outputs and H9-BUNDLE-03 blocked/preflight outputs. Do not make new live source calls by default.

## VALIDATION

Run `git status --short`, `git diff --check`, H9 review-quality validator when added, H9/H8/core validators where practical, `scripts/check_architecture_boundaries.py`, and AIDE Lite checks where practical:

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`

## EVIDENCE

- `control/audits/h9-bundle-03-media-metadata-live-probes-v0/`
- `.aide/queue/H9-BUNDLE-04/task.yaml`
- `.aide/queue/`

## ACCEPTANCE

H9 outputs remain candidates/previews; no source/evidence/candidate/media/music/image/video/map/fingerprint/rights/safety/public truth is accepted.

## NON_GOALS

No new live calls, media downloads/uploads, fingerprinting, scraping, crawling, restricted access, source sync, public/master index mutation, or product behavior changes.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1500
