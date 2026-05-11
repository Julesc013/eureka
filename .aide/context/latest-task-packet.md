# AIDE Latest Task Packet

## PHASE

H9-BUNDLE-01 - Media, music, image, video, and map source-family policy packs. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Start Track H9 by adding policy-pack-only governance for media, music, image, video, and map sources after H8 review integration closed with fixture-equivalent outputs.

## WHY

H8-BUNDLE-04 closes the manuals/docs/standards wave without accepting truth, enabling downloads, or approving future connectors. H9 can now define the next source-family policy layer while J1/K/L remain deferred.

## CONTEXT_REFS

- `control/audits/h8-bundle-04-manuals-docs-review-quality-audit-v0/`
- `control/audits/h8-bundle-03-manuals-docs-live-probes-v0/`
- `control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/`
- `control/audits/h8-bundle-01-manuals-docs-standards-policy-packs-v0/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `AGENTS.md`

## ALLOWED_PATHS

- H9 policy-pack contracts, inventories, examples, docs, scripts, tests, audit pack, and AIDE routing metadata only.
- `.aide/queue/`, `.aide/context/`, and `.aide/reports/` routing metadata updates for the H9 handoff.

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
- document, standards, OCR, full-text, media, restricted-source, repair/action, and local private-state roots
- product runtime behavior outside explicit future H9 policy-pack scope

## IMPLEMENTATION

- Read H8-BUNDLE-04 audit output and H9 task packet context first.
- Add H9 media/music/image/video/map policy-pack-only artifacts.
- Keep H9 work to source records, policy packs, coverage/scorecard previews, docs, validators, tests, and audit evidence.
- Do not enable live probes, source sync, downloads, scraping, crawling, extraction, or truth acceptance.

## VALIDATION

- Run `git status --short`.
- Run `git diff --check`.
- Run the H9 policy-pack validator added by the task.
- Run relevant H8/H7/core validators if present.
- Run focused unit tests and `python scripts/check_architecture_boundaries.py` when runtime or connector boundaries are touched.
- Run AIDE Lite checks where practical.
- Run `.aide/scripts/aide_lite.py doctor`.
- Run `.aide/scripts/aide_lite.py validate`.
- Run `.aide/scripts/aide_lite.py test`.
- Run `.aide/scripts/aide_lite.py selftest`.
- Run `.aide/scripts/aide_lite.py eval run`.
- Run `.aide/scripts/aide_lite.py verify`.

## EVIDENCE

- `control/audits/h8-bundle-04-manuals-docs-review-quality-audit-v0/`
- `.aide/queue/H9-BUNDLE-01/task.yaml`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`

## ACCEPTANCE

- H9 policy-pack scope is explicit and fixture/live runtime behavior remains disabled.
- Media/music/image/video/map source records and policy packs validate.
- No public/master index mutation or product behavior change occurs.
- No source, evidence, candidate, media, rights, access, geospatial, identity, or public truth is accepted.

## NON_GOALS

- No live calls, downloads, scraping, crawling, source sync, public/master index mutation, source/evidence/candidate truth acceptance, or product behavior changes.
- Proceed without changing Eureka product behavior.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1400
