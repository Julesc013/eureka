# AIDE Latest Task Packet

## PHASE

H2-BUNDLE-04 - Package registry review integration and quality delta

## GOAL

Prepare the next Eureka H2 task after H2-BUNDLE-03. This packet is a compact AIDE resumption handoff only; it does not itself authorize code edits or Eureka product behavior changes. A future task prompt must explicitly scope H2-BUNDLE-04 implementation before product paths are edited.

H2-BUNDLE-04 should integrate H2 fixture outputs and blocked live-probe outputs into review previews, quality delta, source-pack update previews, and readiness evidence.

## WHY

H2-BUNDLE-03 established fail-closed metadata-only live-probe contracts, policies, wrappers, examples, tests, docs, and audit evidence. All current H2 package live probes are blocked before network use because no source-specific approval is committed. H2-BUNDLE-02 fixture-equivalent outputs remain available for review integration.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H2-BUNDLE-03/task.yaml`
- `.aide/queue/H2-BUNDLE-04/task.yaml`
- `control/audits/h2-bundle-03-package-live-probes-v0/`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/`
- `scripts/check_architecture_boundaries.py`

## ALLOWED_PATHS

- `.aide/**`
- local-only planning docs or audit notes under `control/audits/**` if a future prompt explicitly scopes them.

## IMPLEMENTATION

- Do not start H2-BUNDLE-04 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h2-bundle-03-package-live-probes-v0/`.
- Treat H2-BUNDLE-03 outputs as blocked/preflight evidence unless a future committed approval artifact exists.
- Preserve no-download, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- This handoff is AIDE operating metadata and should proceed without changing Eureka product behavior.

## ACCEPTANCE

- Latest handoff points to H2-BUNDLE-04.
- H2-BUNDLE-03 evidence remains reviewable.
- AIDE doctor, validate, test, selftest, eval run, and verify are available as local validation lanes.
- No live source calls, package downloads, source sync, public query fanout, public/master index mutation, or product behavior changes are authorized by this handoff.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H2-BUNDLE-04/task.yaml`
- `control/audits/h2-bundle-03-package-live-probes-v0/h2_bundle_03_report.json`
- `control/audits/h2-bundle-03-package-live-probes-v0/validation.md`
- `control/audits/h2-bundle-03-package-live-probes-v0/live_probe_execution_report.md`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/h2_bundle_02_report.json`

## NON_GOALS

- Do not rely on full chat history or pasted whole-repository contents.
- No downloads, installs, execution, scraping, crawling, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, public truth creation, public launch, deployment, or production-readiness claims.
- No live probe execution without explicit committed source approval.

## OUTPUT_SCHEMA

Future H2-BUNDLE-04 responses should preserve status, summary, commits, changed paths, validation, review-integration scope, blocked/live probe status, no-download boundary, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1200
- budget_status: within_budget

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
- `site/dist/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`
- provider secret files
- package cache roots
