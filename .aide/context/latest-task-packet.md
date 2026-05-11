# AIDE Latest Task Packet

## PHASE

H11-BUNDLE-01 - Storefront and app-store source-family policy packs. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Start H11 with policy-pack-only storefront and app-store source-family governance for Eureka after H10 games/emulation review closeout.

## WHY

H10-BUNDLE-04 integrates fixture-equivalent and blocked live-probe outputs into review seeds, quality delta, postmortem, and exit evidence. H10 recommends READY_FOR_H11_BUNDLE_01 without enabling live calls, downloads, uploads, execution, acquisition actions, source sync, index mutation, or truth acceptance.

## CONTEXT_REFS

- `control/audits/h10-bundle-04-games-emulation-review-quality-audit-v0/`
- `control/audits/h10-bundle-03-games-emulation-live-probes-v0/`
- `control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/`
- `control/audits/h10-bundle-01-games-emulation-policy-packs-v0/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/memory/project-state.md`
- `AGENTS.md`

## ALLOWED_PATHS

H11 source-family policy packs, source records, connector-family mappings, docs, examples, validators, audit pack, and `.aide/` operating metadata only when the next reviewed task explicitly scopes them.

## FORBIDDEN_PATHS

- live connector runtime enablement
- product search/public surfaces
- runtime/**
- contracts/**
- surfaces/**
- site/**
- native/**
- crates/**
- connectors/**
- packaging/**
- third_party/**
- runtime behavior changes
- hosted behavior
- source sync
- public index data root
- master-index or publication roots
- storefront account/session roots
- download/upload/private local roots
- native/client behavior

## IMPLEMENTATION

Use H10 review closeout evidence as handoff only. Do not treat H10 fixture replay, blocked live probes, or review seeds as game identity truth, release/platform truth, emulator compatibility truth, hash-set truth, ROM/disc/media truth, action permission, rights/safety truth, evidence acceptance, source truth, public truth, or production readiness.

## VALIDATION

Run H11 policy-pack validators when added, existing H10 review-quality/live-probe/fixture/policy validators, architecture checks, and AIDE Lite checks where practical:

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`
- `scripts/check_architecture_boundaries.py`

## EVIDENCE

- `control/audits/h10-bundle-04-games-emulation-review-quality-audit-v0/`
- `.aide/queue/H11-BUNDLE-01/task.yaml`

## ACCEPTANCE

H11 remains policy-pack-only until reviewed and should proceed without changing Eureka product behavior. H10 closeout preserved no-live-call, no-download, no-upload, no-execute, no-acquisition, no-index-mutation, no-product-behavior-change, and no-truth-acceptance boundaries.

## NON_GOALS

No live source calls, catalog/API/software-list/hash-set fetches, downloads, uploads, hash submissions, execution, acquisition actions, scraping, crawling, restricted-source access, source sync, public/master index mutation, product behavior changes, or model/provider calls.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 800
