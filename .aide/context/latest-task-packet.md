# AIDE Latest Task Packet

## PHASE

H10-BUNDLE-01 - Games, emulation, and software-identity source-family policy packs. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Start H10 with policy-pack-only source-family governance after H9 media metadata review closeout.

## WHY

H9-BUNDLE-04 closes the media metadata wave using fixture-equivalent and blocked live-probe evidence, preserving no-live, no-download/upload/fingerprint, no-truth, and no-index-mutation boundaries.

## CONTEXT_REFS

- `control/audits/h9-bundle-04-media-metadata-review-quality-audit-v0/`
- `control/audits/h9-bundle-03-media-metadata-live-probes-v0/`
- `control/audits/h9-bundle-02-media-metadata-fixture-runtime-v0/`
- `control/audits/h9-bundle-01-media-metadata-policy-packs-v0/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/memory/project-state.md`
- `AGENTS.md`

## ALLOWED_PATHS

H10 policy-pack artifacts requested by the next task, plus `.aide/` routing and operating metadata only. Keep edits narrowly scoped and do the work without changing Eureka product behavior.

## FORBIDDEN_PATHS

- `runtime/**`
- `contracts/**`
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
- download/upload/execution/emulation/private local roots
- product behavior surfaces

## IMPLEMENTATION

Use H9 closeout evidence as the route handoff. Do not make live source calls, downloads, execution, emulation, scraping, crawling, model/provider calls, index mutations, or truth acceptance.

## VALIDATION

Run `git status --short`, `git diff --check`, H10 validators when added, existing H9/H8/core validators where practical, `scripts/check_architecture_boundaries.py`, and AIDE Lite checks where practical:

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`
- `scripts/check_architecture_boundaries.py`

## EVIDENCE

- `control/audits/h9-bundle-04-media-metadata-review-quality-audit-v0/`
- `.aide/queue/H10-BUNDLE-01/task.yaml`
- `.aide/queue/`

## ACCEPTANCE

H10 remains policy-pack-only; no source/evidence/candidate/software identity/public truth is accepted.

## NON_GOALS

No live calls, downloads, execution, emulation, uploads, scraping, crawling, restricted access, source sync, public/master index mutation, product behavior changes, or model/provider calls.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1200
