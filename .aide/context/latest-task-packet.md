# AIDE Latest Task Packet

## PHASE

G-BUNDLE-02 - Ranking shadow runtime and search-quality harness

## GOAL

Continue after G-BUNDLE-01 by using fixture-only Eureka result explanations, near misses, known absence records, and search-gap explanations as inputs to a shadow ranking and search-quality harness.

G-BUNDLE-02 should remain shadow-only. It must not change public search behavior, change public ranking behavior, mutate public/master indexes, accept evidence/candidate/source/public truth, call networks, download files, execute payloads, inspect private files, or call models/providers by default.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not modified by this G-track handoff.

## WHY

G-BUNDLE-01 made explanations and known absence reviewable without making them authoritative. The next task can measure ranking and explanation quality in a fixture-only harness while keeping public ranking untouched.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/G-BUNDLE-01/task.yaml`
- `.aide/queue/G-BUNDLE-02/task.yaml`
- `control/audits/g-bundle-01-result-explanations-absence-v0/`
- `contracts/query/`
- `runtime/search_quality/`
- `examples/search_quality/`
- `docs/architecture/SEARCH_EXPLANATION_MODEL.md`
- `docs/operations/SEARCH_EXPLANATION_NO_RANKING_CHANGE_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the G-BUNDLE-02 prompt.
- G-BUNDLE-01 artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use G-BUNDLE-01 output bundles, explanations, near misses, known absence records, and search-gap explanations as explicit inputs.
- Keep G-BUNDLE-02 fixture-only and shadow-only until a reviewed task packet allows broader behavior.
- Preserve no-ranking-change and no-public-search-mutation boundaries.
- Preserve review gates; shadow-ranking outputs must not become accepted evidence, candidates, public truth, or master-index truth.
- Preserve this handoff without changing Eureka product behavior.

## ACCEPTANCE

- G-BUNDLE-02 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if G-BUNDLE-01 audit artifacts validate and no public search mutation, ranking mutation, network, download, source sync, index mutation, truth acceptance, or Eureka product behavior change is introduced.

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
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`

## VALIDATION

- `python scripts/validate_search_explanation_runtime.py`
- `python scripts/validate_extraction_search_integration.py`
- G-BUNDLE-02-specific validators and tests once defined.
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- G-BUNDLE-01 audit pack: `control/audits/g-bundle-01-result-explanations-absence-v0/`

## NON_GOALS

- No public search behavior change, ranking behavior change, public search runtime mutation, public/master index mutation, candidate/evidence/review store mutation, evidence/candidate/source/public truth acceptance, downloads, live calls, network/API/model/provider calls, file execution, installer runs, source sync, public query fanout, scraping/crawling, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, global absence claims, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

Return the schema requested by the next task prompt.

## TOKEN_ESTIMATE

approx_tokens: 780
