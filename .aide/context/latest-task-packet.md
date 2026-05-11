# AIDE Latest Task Packet

## PHASE

H10-BUNDLE-04 - Games, emulation, and software-identity review integration and quality delta. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Integrate H10 fixture-equivalent and blocked metadata-only live-probe outputs into review seeds, quality delta, connector scorecards, postmortem, and H10 exit evidence.

## WHY

H10-BUNDLE-03 establishes fail-closed, approval-gated metadata-only live-probe envelopes. No live source calls are enabled; blocked and dry fixture-equivalent outputs are sufficient for the review integration rehearsal.

## CONTEXT_REFS

- `control/audits/h10-bundle-03-games-emulation-live-probes-v0/`
- `control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/`
- `control/audits/h10-bundle-01-games-emulation-policy-packs-v0/`
- `runtime/connectors/h10_games_emulation/`
- `examples/connectors/h10_games_emulation/`
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

H10 review integration policies, docs, runtime helpers, scripts, examples, tests, audit pack, and `.aide/` operating metadata only when the next reviewed task explicitly scopes them. Keep the next task to review/quality rehearsal with no Eureka product behavior change.

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
- source sync or hosted behavior
- site distribution output root
- public index data root
- master-index or publication roots
- ROM/ISO/disc-image/emulator/BIOS/game-install/download/upload/execution/private local roots

## IMPLEMENTATION

Use committed H10 fixtures, fixture replay outputs, blocked live-probe reports, and dry preflight examples only. Do not make new live calls, downloads, uploads, execution, acquisition actions, scraping, crawling, restricted access, source sync, public/master index mutation, or truth acceptance.

## VALIDATION

Run H10 review-quality validators when added, existing H10 live-probe, fixture, and policy validators, targeted tests, architecture checks, and AIDE Lite checks where practical:

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`
- `scripts/check_architecture_boundaries.py`

## EVIDENCE

- `control/audits/h10-bundle-03-games-emulation-live-probes-v0/`
- `.aide/queue/H10-BUNDLE-04/task.yaml`

## ACCEPTANCE

H10 review integration remains a rehearsal only and does not accept source, evidence, candidate, game/release/platform/emulator/hash-set/ROM-disc/relation/action/rights/safety/public truth. H10-BUNDLE-04 should preserve no-live-call, no-download, no-upload, no-execute, no-acquisition, no-index-mutation, and no-product-behavior-change boundaries.

## NON_GOALS

No live source calls, catalog/API/software-list/hash-set fetches, downloads, uploads, hash submissions, emulator/game/install execution, acquisition actions, scraping, crawling, restricted-source access, source sync, public/master index mutation, product behavior changes, or model/provider calls.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 900
