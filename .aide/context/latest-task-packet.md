# AIDE Latest Task Packet

## PHASE

D-BUNDLE-02 - Localhost read-only relay and old-browser harness

## GOAL

Continue after D-BUNDLE-01 by preparing the next reviewed D-lane task: a localhost read-only relay and old-browser harness built from verified fixture snapshots.

D-BUNDLE-02 remains review-gated. It must not enable public hosting, deployment, public route activation, live source access, downloads, mirroring, installs, execution, emulation, public/master index mutation, source/evidence/candidate/public truth acceptance, telemetry, or model/provider calls by default.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

This next task should use the D-BUNDLE-01 snapshot substrate without changing Eureka product behavior in public search, hosted, deployment, or index surfaces.

## WHY

D-BUNDLE-01 added fixture snapshot envelopes, deterministic manifests, local fixity, unsigned/placeholder signature-envelope handling, local verification, consumer reports, and text/lite HTML/file-tree renderers. D-BUNDLE-02 can consume those reviewed outputs to design a read-only localhost harness while keeping hosting and public-route behavior disabled until separately approved.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/D-BUNDLE-01/task.yaml`
- `.aide/queue/D-BUNDLE-02/task.yaml`
- `control/audits/d-bundle-01-snapshot-envelope-consumer-renderers-v0/`
- `contracts/snapshots/`
- `runtime/snapshots/`
- `examples/snapshots/`
- `docs/reference/SNAPSHOT_ENVELOPE_CONTRACT.md`
- `docs/operations/SNAPSHOT_TO_RELAY_HANDOFF.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the D-BUNDLE-02 prompt.
- D-BUNDLE-01 snapshot artifacts are read-only context unless the next task explicitly scopes updates.

## IMPLEMENTATION

- Use D-BUNDLE-01 snapshot envelopes, manifests, consumer reports, and render outputs as input context only.
- Preserve no-hosting, no-deployment, no-live-access, no-download, no-mirror, no-install, no-execution, no-emulation, no-truth-acceptance, no-index-mutation, and no-public-search-change boundaries.
- Keep any relay harness local, read-only, review-gated, and off by default until a reviewed D-BUNDLE-02 prompt explicitly scopes implementation.

## ACCEPTANCE

- D-BUNDLE-02 acceptance criteria will be defined by its task prompt.
- The handoff is acceptable only if D-BUNDLE-01 audit artifacts validate and no public route activation, hosting, network access, download, source sync, index mutation, truth acceptance, or product behavior change is introduced.

## FORBIDDEN_PATHS

- Product paths are forbidden by default unless explicitly scoped by the D-BUNDLE-02 prompt and preserved by validation.
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
- `control/inventory/publication/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`

## VALIDATION

- `python scripts/validate_snapshot_runtime.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`
- D-BUNDLE-02-specific validators and tests once defined.

## EVIDENCE

- D-BUNDLE-01 audit pack: `control/audits/d-bundle-01-snapshot-envelope-consumer-renderers-v0/`

## NON_GOALS

- No public search behavior change, ranking behavior change, public/master index mutation, candidate/evidence/review store mutation, evidence/candidate/source/public truth acceptance, downloads, mirroring, installation, execution, emulation, live source access, public hosting, deployment, public route activation, network/API/model/provider calls, uploads/accounts/telemetry, rights-clearance claims, malware-safety claims, verified-installability claims, production-readiness claims, site/dist regeneration, or local private-state roots.

## OUTPUT_SCHEMA

- Next reviewed D-BUNDLE-02 task prompt plus audit evidence.
- No raw prompts, raw responses, secrets, provider keys, or local private state.

## TOKEN_ESTIMATE

- approx_tokens: 1030
- budget_status: within_budget
