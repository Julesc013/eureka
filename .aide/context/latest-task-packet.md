# AIDE Latest Task Packet

## PHASE

F-BUNDLE-02 - Extraction candidate effects and search integration

## GOAL

Continue after F-BUNDLE-01 by refining extraction candidate effects and search integration previews from fixture-only extraction results.

F-BUNDLE-02 should use F-BUNDLE-01 outputs as explicit inputs. It must not inspect private files, download files, execute payloads, call networks, mutate source cache/evidence/review/public/master indexes, accept truth, or change public search behavior by default.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not modified by this F-track handoff.

## WHY

F-BUNDLE-01 added the bounded extraction sandbox for Tier 0 outer metadata, Tier 1 member listing, and Tier 2 manifest-candidate extraction. The next task can connect those preview outputs to search-facing planning artifacts while preserving review gates.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/F-BUNDLE-01/task.yaml`
- `control/audits/f-bundle-01-extraction-sandbox-tier0-2-v0/`
- `contracts/extraction/`
- `runtime/extraction/`
- `examples/extraction/`
- `docs/operations/EXTRACTION_CANDIDATE_EFFECTS.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the F-BUNDLE-02 prompt.
- F-BUNDLE-01 artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use F-BUNDLE-01 extraction result and candidate-effect previews as explicit inputs.
- Keep any F-BUNDLE-02 work fixture-only until a reviewed task packet allows broader behavior.
- Preserve extraction review gates; previews must not become accepted source, evidence, candidate, public, or master-index truth.
- Preserve this handoff without changing Eureka product behavior.

## ACCEPTANCE

- F-BUNDLE-02 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if F-BUNDLE-01 audit artifacts validate and no private-file access, execution, network, download, source sync, or index mutation is introduced.

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

- `python scripts/validate_extraction_sandbox.py`
- F-BUNDLE-02-specific validators and tests once defined.
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- F-BUNDLE-01 audit pack: `control/audits/f-bundle-01-extraction-sandbox-tier0-2-v0/`

## NON_GOALS

- No private file inspection, downloads, live calls, network/API/model/provider calls, file execution, installer runs, recursive deep extraction, source sync, public query fanout, public/master index mutation, evidence/candidate/source/public truth acceptance, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, or local private-state roots.

## OUTPUT_SCHEMA

Return the schema requested by the next task prompt.

## TOKEN_ESTIMATE

approx_tokens: 650
