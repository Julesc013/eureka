# AIDE Latest Task Packet

## PHASE

H4-BUNDLE-02 - Code/source/release host fixture runtimes and normalizers

## GOAL

Prepare the next Eureka H4 task after H4-BUNDLE-01. This packet is a compact AIDE resumption handoff only; it does not itself authorize fixture-runtime implementation or product behavior changes. A future task prompt must explicitly scope H4-BUNDLE-02 implementation before product paths are edited.

H4-BUNDLE-02 should use committed synthetic/repo-local fixtures to normalize code/source/release host metadata without live calls, repository clones, downloads, git/build commands, installs, execution, source sync, public/master index mutation, or truth acceptance.

## WHY

H4-BUNDLE-01 adds policy-pack-only source records, connector-family assignments, identity/release/relation policies, coverage previews, scorecard previews, docs, validators, tests, and audit evidence for ten code/source/release host metadata sources. The next bounded step is fixture replay and normalizer planning.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `.aide/queue/H4-BUNDLE-01/task.yaml`
- `.aide/queue/H4-BUNDLE-02/task.yaml`
- `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/`
- `control/inventory/source_packs/h4_code_source_release_sources.json`
- `control/inventory/source_packs/h4_code_source_release_source_pack_policy.json`
- `control/inventory/source_packs/h4_code_source_release_no_live_call_policy.json`
- `control/inventory/source_packs/h4_code_source_release_no_clone_download_policy.json`
- `scripts/validate_h4_code_source_release_policy_packs.py`
- `scripts/summarize_h4_code_source_release_sources.py`

## ALLOWED_PATHS

- `.aide/**`
- H4 fixture-runtime paths only if a future prompt explicitly scopes H4-BUNDLE-02 implementation.

## IMPLEMENTATION

- Do not start H4-BUNDLE-02 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/`.
- Preserve no-live-call, no-repository-clone, no-source-archive-download, no-release-asset-download, no-git-command, no-build-command, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- H4 fixture runtime should use committed synthetic/repo-local fixtures only.
- No Eureka product behavior change is authorized by this handoff.

## ACCEPTANCE

- Latest handoff points to H4-BUNDLE-02.
- H4-BUNDLE-01 evidence remains reviewable.
- No live source calls, repository clone, source archive downloads, release asset downloads, git command invocation, build tool invocation, installs, execution, source sync, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, source identity truth acceptance, release identity truth acceptance, source-to-binary relation truth acceptance, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h4_code_source_release_policy_packs.py`
- `python scripts/summarize_h4_code_source_release_sources.py --check`
- `python -m unittest tests.operations.test_h4_code_source_release_policy_packs`
- `python -m unittest tests.operations.test_h4_code_source_release_summary`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H4-BUNDLE-01/task.yaml`
- `.aide/queue/H4-BUNDLE-02/task.yaml`
- `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_bundle_01_report.json`
- `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/validation.md`

## NON_GOALS

- No live calls, downloads, installs, execution, scraping, crawling, repository clones, git fetch, git command invocation, build tool invocation, source archive downloads, release asset downloads, binary downloads, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, source identity truth acceptance, release identity truth acceptance, source-to-binary relation truth acceptance, public truth creation, public launch, deployment, or production-readiness claims.

## OUTPUT_SCHEMA

Future H4-BUNDLE-02 responses should preserve status, summary, commits, changed paths, validation, fixture-only scope, no-live/no-clone/no-download/no-git/no-build boundaries, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1000
- budget_status: within_budget

## FORBIDDEN_PATHS

- `surfaces/**`
- `runtime/**`
- `contracts/**`
- `connectors/**`
- `native/**`
- `crates/**`
- `packaging/**`
- `third_party/**`
- `site/**`
- `site/dist/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`
- provider secret files
- package cache roots
- repository clone roots
- repository mirror roots
