# AIDE Latest Task Packet

## PHASE

C-BUNDLE-03 - Native smoke evidence and packaging manifests

## GOAL

Continue after C-BUNDLE-02 by preparing the next reviewed Eureka C-lane task:
native smoke evidence and packaging manifests for the WinForms, Win32, AppKit,
and Carbon read-only native skeletons.

C-BUNDLE-03 remains review-gated. It must not enable live source access,
downloads, mirroring, installs, execution, emulation, public hosting, public
relay, public search behavior changes, public/master index mutation,
source/evidence/candidate/public truth acceptance, accounts, uploads,
telemetry, release artifacts, or committed build outputs by default.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

This packet is a handoff only and proceeds with no Eureka product behavior
change.

## WHY

C-BUNDLE-02 added read-only Win32, AppKit, and Carbon skeletons over the
snapshot, relay, action, blocked-action, and public-safe native contract
surfaces. C-BUNDLE-03 can add packaging-manifest and manual smoke-evidence
governance around those skeletons while preserving the no-download, no-execute,
no-live-access, no-truth-acceptance, and no-index-mutation boundaries.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/C-BUNDLE-02/task.yaml`
- `.aide/queue/C-BUNDLE-03/task.yaml`
- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/`
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/`
- `native/`
- `contracts/native/`
- `control/inventory/native/`
- `docs/architecture/NATIVE_CLIENT_FAMILY_MODEL.md`
- `docs/architecture/NATIVE_SNAPSHOT_RELAY_CONSUMPTION_MODEL.md`
- `docs/operations/NATIVE_READONLY_CLIENT_POLICY.md`
- `docs/operations/NATIVE_NO_DOWNLOAD_EXECUTE_POLICY.md`
- `docs/operations/NATIVE_BUILD_EVIDENCE_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the C-BUNDLE-03 prompt.
- C-BUNDLE-01 and C-BUNDLE-02 native artifacts are read-only context unless
  the next task explicitly scopes updates.

## IMPLEMENTATION

- Use C-BUNDLE-01 and C-BUNDLE-02 native matrix, project, and audit outputs as
  bounded fixture context only.
- Keep native evidence descriptive unless an explicit host build is reviewed and
  produces allowed audit evidence.
- Do not commit build outputs, release binaries, installer payloads, downloaded
  artifacts, or generated IDE caches.
- Do not introduce source connector calls, Python runtime internals, downloads,
  installs, execution, release artifacts, telemetry, or public index writes.

## ACCEPTANCE

- C-BUNDLE-03 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if C-BUNDLE-02 audit artifacts validate and no
  live access, download, source sync, execution, public/master index mutation,
  truth acceptance, product behavior change, release artifact, or build-output
  commit is introduced.

## VALIDATION

- `python scripts/validate_native_matrix.py`
- `python scripts/validate_native_skeleton.py`
- `python scripts/validate_native_c89_library.py`
- `python scripts/validate_native_first_wave_skeletons.py`
- `python scripts/validate_native_project_boundaries.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/`
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/c_bundle_02_report.json`
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/validation.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.md`

## NON_GOALS

- No live source calls.
- No external/API/model/provider calls.
- No downloads, mirroring, installs, execution, or emulation.
- No source sync or public query fanout.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, snapshot, relay, native fixture,
  or public truth acceptance.
- No hosting, public relay, uploads, accounts, telemetry, release binaries,
  build-output commits, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

Future C-BUNDLE-03 task responses should preserve the repo task final schema:
status, summary, commits, changed paths, validation, native scope, readiness,
risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1080
- budget_status: within_budget

## FORBIDDEN_PATHS

- `site/**`
- `contracts/**`
- `runtime/**`
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
