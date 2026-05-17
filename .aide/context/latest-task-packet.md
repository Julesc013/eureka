# AIDE Latest Task Packet

phase: PLAY-00

## PHASE

PLAY-00

## GOAL

Add a small local workbench seed corpus and demo hunt pack so the operator can
test the local workbench loop with predictable local data.

## WHY

INSTANCE-LAYOUT-01 makes the default instance under the sibling instances root canonical.
PLAY-00 should use that explicit local instance path and provide a practical
local play loop without opening source probes, extraction, model providers,
downloads, deployment, or public/production claims.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/latest-context-packet.md`
- `control/inventory/instance_layout_result.json`
- `control/inventory/instance_layout_next_task_decision.json`
- `control/audits/instance-layout-01-v0/`
- `docs/operations/LOCAL_INSTANCE_LAYOUT.md`
- `docs/operations/INSTANCE_PATH_POLICY.md`

## ALLOWED_PATHS

- To be defined by a future PLAY-00 prompt.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `instances/**`
- private local files
- committed operator tokens
- committed provider credentials
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Do not start PLAY-00 from INSTANCE-LAYOUT-01.
- Use the default instance under the sibling instances root as the documented local instance path.
- Keep demo/seed work local and deterministic unless a future task says otherwise.

## VALIDATION

- To be selected from the repo command matrix after PLAY-00 scope is defined.

## EVIDENCE

- `.aide/queue/PLAY-00/`

## NON_GOALS

No source probes, Internet Archive calls, extraction, AI/model/provider calls,
downloads, install/execute behavior, deployment, public launch claim,
production readiness claim, master-index mutation, reviewed-index semantic
mutation, automatic deletion of the legacy sibling instance,
automatic filesystem move outside the repo, or live source/search behavior
changes.

## ACCEPTANCE

- To be defined by a future PLAY-00 prompt.

## OUTPUT_SCHEMA

- To be defined by a future PLAY-00 prompt.

## TOKEN_ESTIMATE

approx_tokens: 850
