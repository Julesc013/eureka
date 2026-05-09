# AIDE Latest Task Packet

## PHASE

C-BUNDLE-01 - Native skeleton, matrix, C89 library, and WinForms proof

## GOAL

Continue after D-BUNDLE-02 by preparing the next reviewed Eureka C-lane task: a native
skeleton and compatibility proof that can consume fixture snapshot/relay
projections without enabling risky actions.

C-BUNDLE-01 remains review-gated. It must not enable public hosting, deployment,
public route activation, live source access, downloads, mirroring, installs,
execution, emulation, public/master index mutation, source/evidence/candidate/
public truth acceptance, telemetry, uploads/accounts, or model/provider calls by
default.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

This packet is a handoff only and proceeds without changing Eureka product behavior.

## WHY

D-BUNDLE-02 added a localhost-only, read-only, fixture-only relay with text,
lite HTML, terminal, and native fixture JSON projections. C-BUNDLE-01 can use
that bounded local compatibility target while keeping public hosting, live
access, unsafe actions, and product behavior changes disabled.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/D-BUNDLE-02/task.yaml`
- `.aide/queue/C-BUNDLE-01/task.yaml`
- `control/audits/d-bundle-02-localhost-readonly-relay-v0/`
- `contracts/relay/`
- `runtime/relay/`
- `examples/relay/`
- `docs/architecture/LOCALHOST_RELAY_MODEL.md`
- `docs/operations/RELAY_READ_ONLY_SECURITY_POLICY.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the C-BUNDLE-01 prompt.
- D-BUNDLE-02 relay artifacts are read-only context unless the next task
  explicitly scopes updates.

## IMPLEMENTATION

- Use D-BUNDLE-02 relay outputs and D-BUNDLE-01 snapshot artifacts as bounded
  fixture context only.
- Preserve no-hosting, no-deployment, no-live-access, no-download, no-mirror,
  no-install, no-execution, no-emulation, no-truth-acceptance, no-index-mutation,
  and no-public-search-change boundaries.
- Keep any native skeleton local, review-gated, and non-executing until a
  reviewed C-BUNDLE-01 prompt explicitly scopes implementation.

## ACCEPTANCE

- C-BUNDLE-01 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if D-BUNDLE-02 audit artifacts validate and no
  public bind, hosting, network access, download, source sync, index mutation,
  truth acceptance, or product behavior change is introduced.

## FORBIDDEN_PATHS

- Product paths are forbidden by default unless explicitly scoped by the
  C-BUNDLE-01 prompt and preserved by validation.
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `site/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`

## VALIDATION

- `python scripts/validate_relay_runtime.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`
- C-BUNDLE-01-specific validators and tests once defined.

## EVIDENCE

- D-BUNDLE-02 audit pack: `control/audits/d-bundle-02-localhost-readonly-relay-v0/`

## NON_GOALS

- No public search behavior change, ranking behavior change, public/master index
  mutation, candidate/evidence/review store mutation, evidence/candidate/source/
  public truth acceptance, downloads, mirroring, installation, execution,
  emulation, live source access, public hosting, deployment, public route
  activation, network/API/model/provider calls, uploads/accounts/telemetry,
  rights-clearance claims, malware-safety claims, verified-installability
  claims, production-readiness claims, site/dist regeneration, or local
  private-state roots.

## OUTPUT_SCHEMA

- Next reviewed C-BUNDLE-01 task prompt plus audit evidence.
- No raw prompts, raw responses, secrets, provider keys, or local private state.

## TOKEN_ESTIMATE

- approx_tokens: 1050
- budget_status: within_budget
