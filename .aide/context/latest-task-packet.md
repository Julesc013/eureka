# AIDE Latest Task Packet

## PHASE

D-BUNDLE-01 - Snapshot envelope, consumer, verification, static/text renderers

## GOAL

Continue after J0-BUNDLE-01 by building the next fixture/static snapshot envelope and read-only consumer scaffolding without changing public search behavior or enabling action execution.

D-BUNDLE-01 must remain review-gated. It must not download files, mirror files, install artifacts, execute files, emulate anything, mutate public/master indexes, accept evidence/candidates/source/public truth, call networks, enable hosting, or call models/providers by default.

## WHY

J0-BUNDLE-01 added safe descriptive action manifests, citation bundles, export manifests, acquisition manifests, preservation manifests, and blocked action reports. D-BUNDLE-01 can consume those reviewed manifest boundaries for snapshot packaging and static/text rendering while keeping risky actions blocked.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/J0-BUNDLE-01/task.yaml`
- `.aide/queue/D-BUNDLE-01/task.yaml`
- `control/audits/j0-bundle-01-safe-actions-manifests-v0/`
- `contracts/actions/`
- `runtime/actions/`
- `examples/actions/`
- `docs/reference/ACTION_MANIFEST_CONTRACT.md`
- `docs/operations/FUTURE_RISKY_ACTIONS_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the D-BUNDLE-01 prompt.
- J0 artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use J0 action manifests and blocked-action boundaries as input context only.
- Preserve no-download, no-mirror, no-install, no-execution, no-emulation, no-truth-acceptance, no-index-mutation, no-public-search-change, and no-hosting boundaries.
- Keep snapshot/static/text outputs review-gated until a reviewed task packet allows broader behavior.

## ACCEPTANCE

- D-BUNDLE-01 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if J0-BUNDLE-01 audit artifacts validate and no public search mutation, network, download, source sync, index mutation, truth acceptance, or product behavior change is introduced.

## FORBIDDEN_PATHS

- `site/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`

## VALIDATION

- `python scripts/validate_safe_actions_runtime.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`
- D-BUNDLE-01-specific validators and tests once defined.

## EVIDENCE

- J0-BUNDLE-01 audit pack: `control/audits/j0-bundle-01-safe-actions-manifests-v0/`

## NON_GOALS

- No public search behavior change, ranking behavior change, public/master index mutation, candidate/evidence/review store mutation, evidence/candidate/source/public truth acceptance, downloads, mirroring, installation, execution, emulation, live calls, network/API/model/provider calls, hosting, uploads/accounts/telemetry, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

Return the schema requested by the next task prompt.

## TOKEN_ESTIMATE

approx_tokens: 850
