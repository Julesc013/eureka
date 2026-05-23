# WorkUnit Contract

`contracts/schema/control/policies/node/work_unit.v0.json` defines the first Eureka WorkUnit record.
A WorkUnit is a portable, replay-safe, policy-scoped task specification for a
future Eureka Node.

## What It Is

A WorkUnit describes bounded work: the type of work, status, scope, required
node modes, required node capabilities, inputs, allowed outputs, review gates,
and idempotency behavior. It is designed so future agents can inspect, validate,
dry-run, resume, or classify a task without losing the policy envelope.

## What It Is Not

A WorkUnit is not a runner, permission grant, source approval, network
authorization, evidence acceptance flow, or master-index mutation. WorkUnit
results are not accepted public truth.

## Types And Statuses

The type registry in
`control/inventory/nodes/workunit_type_registry.json` defines current review
types such as `search_need_review`, `source_lead_inspection`,
`observation_candidate_review`, `candidate_dedup`, and future/deferred types
such as `evidence_pack_drafting_future` and
`approved_metadata_probe_future`.

Current examples may be planned, dry-run-only, ready for manual review,
approval-gated, operator-gated, permission-needed, deferred, policy-blocked, or
blocked. Completed, rejected, and superseded statuses remain future vocabulary.

## Boundaries

Every WorkUnit declares source, network, model-provider, credential, and local
state requirements. Current examples keep all active enablement false. Future
or approval-gated examples can describe requirements only with explicit source
policy, operator approval, review gates, kill-switch, rate/budget posture, and
no-truth boundaries.

Every WorkUnit must preserve:

- no observed baseline creation
- no accepted evidence creation
- no public truth creation
- no master-index mutation
- no rights clearance, malware safety, verified installability, exhaustive
  search, or production readiness claims

## Validation

Run:

```powershell
python scripts/validate_eureka_workunit.py
```

The validator is stdlib-only and read-only. It validates the schema,
inventories, examples, referenced node modes/capabilities, idempotency policy,
review gates, false boundaries, and public-safe fixture posture.
