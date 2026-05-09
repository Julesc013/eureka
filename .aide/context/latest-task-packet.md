# AIDE Latest Task Packet

## PHASE

G-BUNDLE-01 - Result explanations, near misses, and known absence

## GOAL

Continue after F-BUNDLE-02 by turning fixture-only extraction search gaps, review seeds, WorkUnit seeds, and usefulness reports into explanation, near-miss, and known-absence planning artifacts.

G-BUNDLE-01 should use F-BUNDLE-02 outputs as explicit inputs. It must not change public search behavior, mutate public/master indexes, accept evidence/candidate/source/public truth, call networks, download files, execute payloads, inspect private files, or call models/providers by default.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not modified by this G-track handoff.

## WHY

F-BUNDLE-02 made extraction findings reviewable without making them true. The next task can explain how hidden members, manifests, blocked extractions, and future-deepening needs affect search gaps while keeping all results as fixture-only previews.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/F-BUNDLE-02/task.yaml`
- `.aide/queue/G-BUNDLE-01/task.yaml`
- `control/audits/f-bundle-02-extraction-candidate-search-integration-v0/`
- `contracts/extraction/`
- `runtime/extraction/`
- `examples/extraction/`
- `docs/operations/EXTRACTION_TO_SEARCH_GAPS.md`
- `docs/operations/EXTRACTION_TO_TRACK_G_HANDOFF.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the G-BUNDLE-01 prompt.
- F-BUNDLE-02 artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use F-BUNDLE-02 extraction search integration, gap, review seed, WorkUnit seed, and usefulness outputs as explicit inputs.
- Keep G-BUNDLE-01 fixture-only until a reviewed task packet allows broader behavior.
- Preserve review gates; explanation and absence artifacts must not become accepted source, evidence, candidate, public, or master-index truth.
- Preserve this handoff without changing Eureka product behavior.

## ACCEPTANCE

- G-BUNDLE-01 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if F-BUNDLE-02 audit artifacts validate and no public search mutation, private-file access, execution, network, download, source sync, index mutation, or truth acceptance is introduced.

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

- `python scripts/validate_extraction_search_integration.py`
- `python scripts/validate_extraction_sandbox.py`
- G-BUNDLE-01-specific validators and tests once defined.
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- F-BUNDLE-02 audit pack: `control/audits/f-bundle-02-extraction-candidate-search-integration-v0/`

## NON_GOALS

- No public search behavior change, public search runtime mutation, public/master index mutation, candidate/evidence/review store mutation, evidence/candidate/source/public truth acceptance, private file inspection, downloads, live calls, network/API/model/provider calls, file execution, installer runs, recursive deep extraction, source sync, public query fanout, scraping/crawling, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, or local private-state roots.

## OUTPUT_SCHEMA

Return the schema requested by the next task prompt.

## TOKEN_ESTIMATE

approx_tokens: 760
