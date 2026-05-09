# AIDE Latest Task Packet

## PHASE

C-BUNDLE-02 - Win32 AppKit Carbon read-only skeletons

## GOAL

Continue after C-BUNDLE-01 by preparing the next reviewed Eureka C-lane task:
read-only Win32, AppKit, and Carbon skeletons over the native matrix, C89
contract helper, snapshot contracts, relay fixture envelopes, and safe action
manifests.

C-BUNDLE-02 remains review-gated. It must not enable live source access,
downloads, mirroring, installs, execution, emulation, public hosting, public
relay, public search behavior changes, public/master index mutation,
source/evidence/candidate/public truth acceptance, accounts, uploads,
telemetry, or release artifacts by default.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

This packet is a handoff only and proceeds with no Eureka product behavior
change.

## WHY

C-BUNDLE-01 added the governed `native/` skeleton, native matrix contracts and
policies, a bounded C89 contract helper library, validators, tests, and a
fixture-oriented WinForms proof. C-BUNDLE-02 can extend the same consumer-only
model to Win32, AppKit, and Carbon skeletons while preserving the no-download,
no-execute, no-live-access, no-truth-acceptance, and no-index-mutation
boundaries.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/C-BUNDLE-01/task.yaml`
- `.aide/queue/C-BUNDLE-02/task.yaml`
- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/`
- `native/`
- `contracts/native/`
- `control/inventory/native/`
- `docs/architecture/NATIVE_CLIENT_FAMILY_MODEL.md`
- `docs/architecture/NATIVE_SNAPSHOT_RELAY_CONSUMPTION_MODEL.md`
- `docs/operations/NATIVE_READONLY_CLIENT_POLICY.md`
- `docs/operations/NATIVE_NO_DOWNLOAD_EXECUTE_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the C-BUNDLE-02 prompt.
- C-BUNDLE-01 native artifacts are read-only context unless the next task
  explicitly scopes updates.

## IMPLEMENTATION

- Use C-BUNDLE-01 native matrix and C89 helper outputs as bounded fixture
  context only.
- Preserve the native directory doctrine: API/toolchain names in paths; support
  state in matrix files.
- Keep Win32, AppKit, and Carbon skeletons read-only and contract-facing.
- Do not introduce source connector calls, Python runtime internals, downloads,
  installs, execution, release artifacts, or public index writes.

## ACCEPTANCE

- C-BUNDLE-02 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if C-BUNDLE-01 audit artifacts validate and no
  live access, download, source sync, execution, public/master index mutation,
  truth acceptance, product behavior change, or build-output commit is
  introduced.

## VALIDATION

- `python scripts/validate_native_matrix.py`
- `python scripts/validate_native_skeleton.py`
- `python scripts/validate_native_c89_library.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/`
- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/c_bundle_01_report.json`
- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/validation.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.md`

## NON_GOALS

- No live source calls.
- No external/API/model/provider calls.
- No downloads, mirroring, installs, execution, or emulation.
- No source sync or public query fanout.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, or public truth acceptance.
- No hosting, public relay, uploads, accounts, telemetry, release binaries,
  build-output commits, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

Future C-BUNDLE-02 task responses should preserve the repo task final schema:
status, summary, commits, changed paths, validation, native scope, readiness,
risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 950
- budget_status: within_budget

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
