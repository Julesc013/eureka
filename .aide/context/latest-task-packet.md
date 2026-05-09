# AIDE Latest Task Packet

## PHASE

E-BUNDLE-01 - Hosting and operations readiness

## GOAL

Continue after C-BUNDLE-03 by preparing the next reviewed Eureka E-lane task:
hosting and operations readiness.

This handoff does not enable hosting. E-BUNDLE-01 must remain review-gated and
must not deploy, regenerate generated site distribution output, bind a public relay, call live sources,
download files, install artifacts, execute artifacts, enable uploads, accounts,
telemetry, public index mutation, master index mutation, or source/evidence/
candidate/public truth acceptance by default.

This packet is a handoff only and proceeds with no Eureka product behavior
change.

## WHY

C-BUNDLE-03 closed the first-wave native readiness track with smoke evidence
packets, packaging manifests, artifact manifests, release-candidate previews,
and a Track C integration audit. The next safe lane is E-BUNDLE-01, which should
turn those reviewed snapshot, relay, action, and native artifacts into hosting
and operations readiness evidence without enabling public hosting behavior.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/C-BUNDLE-03/task.yaml`
- `.aide/queue/E-BUNDLE-01/task.yaml`
- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/`
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/`
- `control/audits/d-bundle-01-snapshot-envelope-consumer-renderers-v0/`
- `control/audits/d-bundle-02-localhost-readonly-relay-v0/`
- `native/`
- `contracts/native/`
- `contracts/relay/`
- `contracts/snapshots/`
- `contracts/actions/`
- `docs/operations/NATIVE_TO_HOSTING_HANDOFF.md`
- `docs/architecture/NATIVE_FIRST_WAVE_INTEGRATION_MODEL.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the E-BUNDLE-01 prompt.
- C/D/J/I artifacts are read-only context unless the next task explicitly
  scopes updates.

## IMPLEMENTATION

- Use C-BUNDLE-03 audit evidence as the Track C exit gate context.
- Keep hosting and operations material as readiness evidence until a future
  reviewed task explicitly enables deployment behavior.
- Do not create hosted runtime state, deployment outputs, public route
  activation, provider calls, credentials, telemetry, accounts, uploads, or
  public search behavior changes.

## ACCEPTANCE

- E-BUNDLE-01 acceptance criteria will be defined by its task prompt.
- This handoff is acceptable only if C-BUNDLE-03 validation remains PASS and no
  release binary, build output, hosted behavior, public relay, live access,
  public/master index mutation, truth acceptance, product behavior change, or
  production-readiness claim is introduced.

## VALIDATION

- `python scripts/validate_native_packaging_manifests.py`
- `python scripts/audit_track_c_integration.py --check`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/c-bundle-03-native-smoke-packaging-v0/`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/c_bundle_03_report.json`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/validation.md`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/track_c_exit_gate_decision.md`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/e_bundle_01_readiness_recommendation.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.md`

## NON_GOALS

- No deployment or hosting enablement.
- No public relay or public bind.
- No live source calls, external/API/model/provider calls, or source sync.
- No downloads, mirroring, installs, execution, or emulation.
- No uploads, accounts, telemetry, or credentials.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, snapshot, relay, native fixture,
  or public truth acceptance.
- No release binaries, build-output commits, generated site output regeneration, local
  private-state roots, rights-clearance claims, malware-safety claims, verified
  installability claims, or production-readiness claims.

## OUTPUT_SCHEMA

Future E-BUNDLE-01 task responses should preserve the repo task final schema:
status, summary, commits, changed paths, validation, hosting/ops scope,
readiness, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1120
- budget_status: within_budget

## FORBIDDEN_PATHS

- `contracts/**`
- `runtime/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- generated site distribution output
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`
