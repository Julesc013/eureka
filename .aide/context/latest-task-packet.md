# AIDE Latest Task Packet

## PHASE

J0-BUNDLE-01 - Safe actions, manifests, citation, and export

## GOAL

Continue after I-BUNDLE-01 by adding reviewed safe-action, manifest, citation, and export scaffolding for Eureka without changing Eureka product behavior.

J0-BUNDLE-01 must remain review-gated. It must not execute actions, run installers, upload files, import or submit packs, accept packs, accept evidence/candidates/source/public truth, mutate public/master indexes, call networks, download files, enable hosted flows, or call models/providers by default.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not modified by this J0-track handoff.

## WHY

I-BUNDLE-01 created local pack quarantine, fixity, signature-envelope validation, import previews, and contribution review seeds without accepting truth. The next task can define safe exported action and citation scaffolding while keeping all effectful operations blocked.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/I-BUNDLE-01/task.yaml`
- `.aide/queue/J0-BUNDLE-01/task.yaml`
- `control/audits/i-bundle-01-pack-quarantine-contribution-review-v0/`
- `contracts/packs/`
- `runtime/local_foundry/`
- `examples/pack_quarantine/`
- `docs/reference/PACK_QUARANTINE_RUNTIME.md`
- `docs/operations/PACK_IMPORT_PREVIEW_NO_IMPORT_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the J0-BUNDLE-01 prompt.
- I-BUNDLE-01 artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use I-BUNDLE-01 quarantine outputs and J0 task prompt as input context only.
- Keep J0 safe actions and exports review-gated until a reviewed task packet allows broader behavior.
- Preserve no-execution, no-upload, no-pack-import, no-pack-submission, no-truth-acceptance, no-index-mutation, and no-public-search-change boundaries.
- Preserve this handoff without changing Eureka product behavior.

## ACCEPTANCE

- J0-BUNDLE-01 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if I-BUNDLE-01 audit artifacts validate and no public ranking/search mutation, network, download, source sync, index mutation, pack acceptance, pack import, truth acceptance, or Eureka product behavior change is introduced.

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

- `python scripts/validate_pack_quarantine_runtime.py`
- `python scripts/validate_pack_export_runtime.py`
- `python scripts/validate_pack_builder_runtime.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`
- J0-BUNDLE-01-specific validators and tests once defined.

## EVIDENCE

- I-BUNDLE-01 audit pack: `control/audits/i-bundle-01-pack-quarantine-contribution-review-v0/`

## NON_GOALS

- No public search behavior change, ranking behavior change, public/master index mutation, candidate/evidence/review store mutation, pack import, pack submission, pack publication, hosted upload, pack acceptance, evidence/candidate/source/public truth acceptance, downloads, live calls, network/API/model/provider calls, file execution, installer runs, source sync, public query fanout, scraping/crawling, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

Return the schema requested by the next task prompt.

## TOKEN_ESTIMATE

approx_tokens: 900
