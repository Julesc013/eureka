# Structure Guardrail Closeout

Task: `STRUCTURE-GUARDRAIL-CLOSEOUT-00`

This closeout freezes the current repository root model and records the guardrails
for future work. It is not a broad directory refactor, a root-move task, a
public launch task, or a source/provider expansion task.

## Authority Note

The live queue/task packet currently recommends
`IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`. This closeout records the structure
decision requested by the operator without mutating `.aide/queue/` or claiming
that the queue recommendation has changed.

Launch-track planning still points to `PUBLIC-ALPHA-OPS-POSTURE-00` as the next
public-alpha blocker to close when the objective is public launch. That is a
launch-track decision, not a silent queue override.

## Frozen Root Model

Accepted active roots:

```text
.aide/
.github/
archive/
contracts/
control/
crates/
docs/
evals/
examples/
external/
native/
release/
runtime/
scripts/
site/
snapshots/
surfaces/
tests/
tools/
```

Classified top-level exception:

```text
.aide.local.example/
```

`.aide.local.example/` is a committed local-state template for AIDE Lite. It is
not an active product root.

## Forbidden Active Roots

Do not add active top-level roots named:

```text
apps/
common/
data/
engine/
experimental/
helpers/
infra/
misc/
modules/
plugins/
renderers/
services/
skins/
temp/
tmp/
utils/
```

If one of those concepts appears in future work, it must fit under an existing
root or receive an explicit future repo-layout contract change.

## Concept Placement

| Concept | Correct home |
| --- | --- |
| Renderer | `runtime/surface/renderers/` |
| Skin | `site/assets/skins/`, `examples/skins/`, or `contracts/representation/` |
| Source family | `runtime/connectors/` plus `contracts/source/families/` |
| Public page | `surfaces/web/`, `site/pages/`, and `contracts/view/` |
| API response | `contracts/api/`, `surfaces/api/`, and `runtime/gateway/` |
| Policy | `contracts/policy/` and `control/policies/` |
| Deployment or ops | `release/`, `docs/operations/`, `control/inventory/hosting/`, or `external/` |
| Plugin family | Specific contracts/runtime family; not a generic `plugins/` root |

## AIDE And Control Boundary

`.aide/` remains repo-operating metadata for task packets, compact context,
reports, adapters, and validation support. It is not product truth.

`control/audits/` remains evidence and audit material. It is not runtime truth
and must not define product behavior by itself.

Product behavior must not depend on `.aide/` reports or `control/audits/`
content unless the meaning is separately promoted through accepted contracts,
runtime behavior, reviewed records, or accepted architecture documents.

## Invariants To Preserve

- Renderers do not invent facts.
- Renderers do not decide policy.
- Renderers expose required status, evidence, and action posture.
- Old-browser, text, file, and lite renderers preserve route identity.
- Source adapters do not own review or promotion.
- Surfaces do not import engine internals outside allowed gateway/interface boundaries.
- Shim paths cannot receive new implementation unless a future task explicitly reclassifies them.
- Generated outputs are either governed artifacts or ignored local state.

## Generated Output Boundary

Tracked root and structure checks are not release proof for generated outputs.
Dedicated validators still own generated artifact cleanliness:

```powershell
python scripts/check_generated_artifact_cleanliness.py --check --json
```

Full unittest discovery remains an external promotion/manual lane and must not
run inside normal AI sessions by default.

## Guardrail Command

`python scripts/check_architecture_boundaries.py` now reports the frozen root
model as part of the architecture-boundary check. The dedicated repo-layout
canon validator remains:

```powershell
python scripts/validate_repo_structure_canon.py --strict --json
```

## Non-Claims

This closeout does not claim public launch readiness, production readiness,
release promotion, full-discovery completion, rights clearance, binary safety,
download safety, or source/provider expansion.
