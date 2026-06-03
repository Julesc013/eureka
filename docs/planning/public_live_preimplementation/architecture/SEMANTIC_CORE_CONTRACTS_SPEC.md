# Semantic Core Contracts Spec

## Current Repo Alignment

TSIS-00 already added semantic, action, route, representation, view, surface,
and policy contracts. Future semantic work should be a gap audit first.

Primary existing paths:

- `contracts/semantic/status.v0.json`
- `contracts/semantic/affordance.v0.json`
- `contracts/action/action_registry.v0.json`
- `contracts/route/route_model.v0.json`
- `contracts/representation/**`
- `contracts/view/**`

## Required Semantics

Every user-visible result must have one canonical status. Every user-visible
action must come from an action/affordance registry and be filtered by policy.

Canonical statuses:

```text
verified candidate need near_miss mention_only policy_blocked private_local
superseded rejected unknown
```

Canonical affordances:

```text
view inspect_evidence compare cite export_manifest watch_need report_issue
review_candidate promote reject rebuild_index
```

## Implementation Gate

If existing contracts differ, implement a governed contract migration or mapping
task before fallback emits public view models.

