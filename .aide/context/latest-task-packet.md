# AIDE Latest Task Packet

## PHASE

UNSPECIFIED - H8-BUNDLE-01 - Manuals, technical docs, datasheets, and standards source-family policy packs. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

H8-BUNDLE-01 - Manuals, technical docs, datasheets, and standards source-family policy packs. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

H7-BUNDLE-04 closed the library/cultural/research review integration wave with fixture-equivalent outputs, blocked-live-probe evidence, quality delta, postmortem, and H8 routing.

## CONTEXT_REFS

- `.aide/queue/H8-BUNDLE-01/task.yaml`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `control/audits/h7-bundle-04-library-research-review-quality-audit-v0/`
- `control/audits/h7-bundle-03-library-research-live-probes-v0/`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `AGENTS.md`

## ALLOWED_PATHS

- `<fill from the next reviewed H8 queue packet>`
- `.aide/context/**`
- `.aide/queue/H8-BUNDLE-01/**`
- `.aide/queue/index.yaml`
- `.aide/reports/eureka-repo-health.*`
- root docs only when behavior or documentation links change

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `site/dist/**`
- `data/public_index/**`
- live source outputs, local private roots, provider secret files, harvested payload roots, download roots, OCR roots, or media roots

## IMPLEMENTATION

- Read the next reviewed H8 queue packet before opening H8 work.
- Keep H8 policy-pack work policy-only until a future task explicitly broadens scope.
- Work without changing Eureka product behavior.
- Preserve H7 review boundaries: no live calls, harvests, queries, fetches, downloads, source sync, public/master index mutation, or truth acceptance.
- Do not treat H7 fixture replay or blocked live-probe reports as production coverage or approval.

## EVIDENCE

- H7 closeout audit: `control/audits/h7-bundle-04-library-research-review-quality-audit-v0/`
- H7 review examples: `examples/connectors/h7_library_research/review_integration/`
- H7 validator: `scripts/validate_h7_library_research_review_quality_audit.py`

## NON_GOALS

- No live source calls.
- No OAI-PMH harvests, DOI/ISBN/library/research/patent API queries, full-text/PDF/book/article/dataset/patent/IIIF/media fetches, scraping, crawling, bypass, restricted-source access, source sync, public/master index mutation, truth acceptance, or production readiness claims.

## ACCEPTANCE

- H8-BUNDLE-01 may start only after H7-BUNDLE-04 passes or passes with warnings and recommends `READY_FOR_H8_BUNDLE_01`.
- J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicitly opened by future reviewed gates.

## OUTPUT_SCHEMA

- final_status: `PASS|PASS_WITH_WARNINGS|PARTIAL|BLOCKED|FAIL`
- next_task: `H8-BUNDLE-01`
- public_index_mutated: `false`
- master_index_mutated: `false`

## VALIDATION

- `python scripts/validate_h7_library_research_review_quality_audit.py`
- `python scripts/audit_h7_library_research_wave.py --check`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## TOKEN_ESTIMATE

- approx_tokens: 520
- method: chars / 4, rounded up
- budget_status: PASS
