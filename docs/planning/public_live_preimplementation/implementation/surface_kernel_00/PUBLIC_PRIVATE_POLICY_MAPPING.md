# Public / Private Policy Mapping

## Public Posture

Public projections are read-only and permit only safe actions:

```text
view
inspect_evidence
compare
cite
export_manifest
```

Public projections remove operator/private fields such as:

```text
operator_actions
allowed_ledger_decisions
auth_boundary
review_handoff
raw_internal_diagnostics
private_local_path_refs
debug
```

Public projections block write/operator/source-control actions including review, promotion, rebuild, download, install, extraction, record mutation, source crawl, and arbitrary live lookup actions.

## Private / Operator Posture

Private projections keep existing Workbench/operator action posture from current Workbench projection payloads.

SurfaceKernel does not implement auth. It only labels private posture and keeps it out of public projection.

## Status Mapping

| Input | Surface Status |
|---|---|
| `verified` | `verified` |
| `candidate` | `candidate` |
| `need` | `need` |
| `policy_blocked` | `policy_blocked` |
| `unavailable` | `unavailable` |
| `degraded` | `unavailable` |
| unknown/missing | `unknown` |

Fallback candidates remain candidates. Fallback needs remain needs. Unknown states do not become verified or absence claims.
