# AIDE Latest Task Packet

## PHASE

H10-BUNDLE-03 - Games, emulation, and software-identity approved metadata-only live probes. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Prepare fail-closed, approval-gated H10 games/emulation metadata-only live-probe envelopes after H10-BUNDLE-02 fixture runtime validation.

## WHY

H10-BUNDLE-02 establishes committed-fixture-only parsing, normalization, candidate previews, source-cache/evidence previews, replay reports, and boundary validation for H10 games/emulation metadata.

## CONTEXT_REFS

- `control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/`
- `control/audits/h10-bundle-01-games-emulation-policy-packs-v0/`
- `control/inventory/source_packs/h10_games_emulation_sources.json`
- `runtime/connectors/h10_games_emulation/`
- `examples/connectors/h10_games_emulation/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/memory/project-state.md`
- `AGENTS.md`

## ALLOWED_PATHS

H10 live-probe policy/envelope artifacts requested by the next task, plus `.aide/` routing and operating metadata only. Keep edits narrowly scoped without changing Eureka product behavior.

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
- site distribution output root
- public index data root
- master-index or publication roots
- ROM/ISO/disc-image/emulator/BIOS/game-install/download/upload/execution/private local roots

## IMPLEMENTATION

Default to offline preflight and blocked output. Do not make live source calls unless future committed source-specific policy explicitly approves one exact bounded metadata-only request; downloads, uploads, execution, emulation, acquisition actions, scraping, crawling, model/provider calls, index mutations, and truth acceptance remain forbidden.

## VALIDATION

Run H10 live-probe validators when added, existing H10 fixture and policy-pack validators, `scripts/check_architecture_boundaries.py`, and AIDE Lite checks where practical:

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`

## EVIDENCE

- `control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/`
- `.aide/queue/H10-BUNDLE-03/task.yaml`

## ACCEPTANCE

H10 live-probe framework remains fail-closed by default and preserves no-download/no-upload, no-execute, no-acquisition, no-index-mutation, and no-truth boundaries.

## NON_GOALS

No broad live calls, downloads, uploads, execution, emulation, acquisition actions, scraping, crawling, restricted access, source sync, public/master index mutation, product behavior changes, or model/provider calls.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1200
