# AIDE Latest Task Packet

## PHASE

I-BUNDLE-01 - Pack quarantine, signed verification, and contribution review

## GOAL

Continue after G-BUNDLE-02 by adding governed pack quarantine, signed verification, and contribution review safeguards for Eureka without changing Eureka product behavior.

I-BUNDLE-01 must remain review-gated. It must not accept packs, mutate public/master indexes, accept evidence/candidate/source/public truth, call networks, download files, execute payloads, inspect private files, enable public ranking, or call models/providers by default.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not modified by this I-track handoff.

## WHY

G-BUNDLE-02 made local shadow ranking measurable without public ranking changes. The next task can add pack quarantine and verification gates before any contribution can influence search, evidence, or index state.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/G-BUNDLE-02/task.yaml`
- `.aide/queue/I-BUNDLE-01/task.yaml`
- `control/audits/g-bundle-02-ranking-shadow-quality-harness-v0/`
- `contracts/query/`
- `runtime/search_quality/`
- `examples/search_quality/`
- `docs/architecture/RANKING_SHADOW_MODEL.md`
- `docs/operations/PUBLIC_RANKING_GATE_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the I-BUNDLE-01 prompt.
- G-BUNDLE-02 artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use G-BUNDLE-02 shadow-ranking outputs and public gate evidence as input context only.
- Keep I-BUNDLE-01 quarantine/review-gated until a reviewed task packet allows broader behavior.
- Preserve no-pack-acceptance, no-index-mutation, no-truth-acceptance, and no-public-ranking-change boundaries.
- Preserve this handoff without changing Eureka product behavior.

## ACCEPTANCE

- I-BUNDLE-01 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if G-BUNDLE-02 audit artifacts validate and no public ranking/search mutation, network, download, source sync, index mutation, pack acceptance, truth acceptance, or Eureka product behavior change is introduced.

## FORBIDDEN_PATHS

- `site/**`
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`

## VALIDATION

- `python scripts/validate_ranking_shadow_runtime.py`
- `python scripts/validate_search_explanation_runtime.py`
- I-BUNDLE-01-specific validators and tests once defined.
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- G-BUNDLE-02 audit pack: `control/audits/g-bundle-02-ranking-shadow-quality-harness-v0/`

## NON_GOALS

- No public search behavior change, ranking behavior change, public search runtime mutation, public/master index mutation, candidate/evidence/review store mutation, pack acceptance, evidence/candidate/source/public truth acceptance, downloads, live calls, network/API/model/provider calls, file execution, installer runs, source sync, public query fanout, scraping/crawling, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

Return the schema requested by the next task prompt.

## TOKEN_ESTIMATE

approx_tokens: 820
