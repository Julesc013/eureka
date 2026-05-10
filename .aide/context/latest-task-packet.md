# AIDE Latest Task Packet

## PHASE

H3-BUNDLE-01 - OS package archive source-family policy packs

## GOAL

Prepare the next Eureka H3 task after H2-BUNDLE-04. This packet is a compact AIDE resumption handoff only; it does not itself authorize code edits or Eureka product behavior changes. A future task prompt must explicitly scope H3-BUNDLE-01 implementation before product paths are edited.

H3-BUNDLE-01 should define OS package archive source-family policy packs after H2 package registry review integration closes.

## WHY

H2-BUNDLE-04 integrated package-registry fixture outputs and blocked live-probe outputs into review seeds, quality delta, postmortem, integration audit, and a next-phase recommendation. H2 live probes remain blocked by missing source-specific operator approval, and no live evidence is inferred.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H2-BUNDLE-04/task.yaml`
- `.aide/queue/H3-BUNDLE-01/task.yaml`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `control/audits/h2-bundle-04-package-review-quality-audit-v0/`
- `control/audits/h2-bundle-03-package-live-probes-v0/`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/`
- `scripts/check_architecture_boundaries.py`

## ALLOWED_PATHS

- `.aide/**`
- local-only planning docs or audit notes under `control/audits/**` if a future prompt explicitly scopes them.

## IMPLEMENTATION

- Do not start H3-BUNDLE-01 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h2-bundle-04-package-review-quality-audit-v0/`.
- Treat H2 live-probe outputs as blocked/preflight evidence unless a future committed approval artifact exists.
- Preserve no-download, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- This handoff is AIDE operating metadata and should proceed without changing Eureka product behavior.

## ACCEPTANCE

- Latest handoff points to H3-BUNDLE-01.
- H2-BUNDLE-04 evidence remains reviewable.
- AIDE doctor, validate, test, selftest, eval run, and verify are available as local validation lanes.
- No live source calls, package downloads, package-manager invocation, source sync, public query fanout, public/master index mutation, truth acceptance, or product behavior changes are authorized by this handoff.

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
- `.aide/queue/H3-BUNDLE-01/task.yaml`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `control/audits/h2-bundle-04-package-review-quality-audit-v0/h2_bundle_04_report.json`
- `control/audits/h2-bundle-04-package-review-quality-audit-v0/validation.md`
- `control/audits/h2-bundle-04-package-review-quality-audit-v0/h2_exit_gate_decision.md`
- `control/audits/h2-bundle-04-package-review-quality-audit-v0/next_phase_recommendation.md`

## NON_GOALS

- Do not rely on full chat history or pasted whole-repository contents.
- No downloads, installs, execution, scraping, crawling, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, dependency correctness acceptance, public truth creation, public launch, deployment, or production-readiness claims.
- No live probe execution without explicit committed source approval.

## OUTPUT_SCHEMA

Future H3-BUNDLE-01 responses should preserve status, summary, commits, changed paths, validation, H3 policy-pack scope, no-download boundary, risks, and next task.

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
