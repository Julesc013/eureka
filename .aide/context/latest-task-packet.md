# AIDE Latest Task Packet

## PHASE

H2-BUNDLE-01 - Package registry source-family policy packs

## GOAL

Begin the next local non-deploy source expansion wave selected by LOCAL-MVP-ITERATION-01. H2 should add package registry source-family policy packs for Maven Central, NuGet, crates.io, RubyGems, CPAN, CRAN, conda-forge, and OCI registry metadata while preserving the H0/H1 source-family policy pattern.

This packet is a Eureka AIDE resumption handoff only and must proceed without changing Eureka product behavior until a future H2 task prompt explicitly scopes implementation. H2 remains local and metadata-first. It must not deploy, launch, call providers, change DNS, enable hosting, enable public relay, mutate generated site output, perform live source fanout, enable source sync, download, upload, install, execute, mirror, emulate, mutate public/master indexes, accept source/evidence/candidate truth, or claim rights clearance, malware safety, installability, production readiness, or public launch.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

LOCAL-MVP-ITERATION-01 selected H2 as the highest-value non-deploy local expansion after the MVP alpha and public-alpha deployment-planning packets. H3, J1, K, L, and deployment execution remain deferred behind explicit gates.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/LOCAL-MVP-ITERATION-01/task.yaml`
- `.aide/queue/H2-BUNDLE-01/task.yaml`
- `control/audits/local-mvp-iteration-01-v0/`
- `control/audits/public-alpha-deployment-plan-01-v0/`
- `control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/`
- `control/audits/h1-bundle-04-review-quality-audit-v0/`

## ALLOWED_PATHS

- `.aide/**`
- local-only planning docs or audit notes under `control/audits/**` if a future prompt explicitly scopes them.

## IMPLEMENTATION

- Follow H0/H1 source-family policy-pack patterns.
- Keep package registry expansion policy-pack and metadata-first.
- Do not perform live source calls or source sync.
- Do not enable downloads, install, execute, mirror, or emulate actions.
- Preserve deployment deferral and no-truth boundaries.

## ACCEPTANCE

- H2 work remains non-deploy and local.
- Package registry source-family policy packs are reviewable without enabling source runtime behavior.
- Public/master indexes and product runtime behavior remain unchanged.

## VALIDATION

- `python scripts/validate_local_mvp_iteration.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/local-mvp-iteration-01-v0/local_mvp_iteration_01_report.json`
- `control/audits/local-mvp-iteration-01-v0/recommended_next_task.md`
- `control/audits/local-mvp-iteration-01-v0/deployment_deferral_review.md`
- `control/audits/local-mvp-iteration-01-v0/validation.md`

## NON_GOALS

- No deployment or launch.
- No provider API calls, provider credentials, secrets, DNS changes, or custom domain claims.
- No public relay, public bind, live source calls, source sync, or public query fanout.
- No downloads, mirroring, installs, execution, or emulation.
- No uploads, accounts, telemetry, or credential collection.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, snapshot, relay, native fixture, or public truth acceptance.
- No generated site output regeneration, local private-state roots, rights-clearance claims, malware-safety claims, verified installability claims, public alpha live claims, production claims, or inferred signoff.

## OUTPUT_SCHEMA

Future H2 responses should preserve status, summary, commits, changed paths, validation, source-family scope, no-deploy boundary, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1000
- budget_status: within_budget

## FORBIDDEN_PATHS

- `site/dist/**`
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
