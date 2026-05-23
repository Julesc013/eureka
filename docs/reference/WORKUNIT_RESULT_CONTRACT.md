# WorkUnit Result Contract

`contracts/schema/control/policies/node/work_unit_result.v0.json` defines the first Eureka WorkUnit
result envelope.

## What It Is

A WorkUnit result records what happened or what would happen for a future
WorkUnit: planned actions, executed validation-only actions, skipped actions,
blocked actions, checked forbidden actions, observed inputs, proposed outputs,
validation summaries, idempotency results, recovery posture, review gates, and
truth boundaries.

## What It Is Not

A WorkUnit result is not a WorkUnit runner, source approval, network
authorization, model/provider call, local state write, review runtime, accepted
evidence, public truth, rights clearance, malware safety, verified
installability, exhaustive search proof, production readiness claim, or
master-index mutation.

## Statuses

Result status vocabulary includes `pass`, `pass_with_warnings`, `warn`,
`partial`, `fail`, `blocked`, `noop`, `skipped`, `deferred`,
`policy_blocked`, `rights_blocked`, `risk_blocked`, `permission_needed`,
`operator_gated`, `human_operated`, `approval_gated`, and `not_evaluable`.

`pass_with_warnings` is valid only when errors are zero and warnings are
documented. `noop` records a validated repeated WorkUnit without changes.
`partial` records resumable work. Blocked statuses record why progress stopped.

## Output Model

Outputs may be reports, observation candidates, source leads, SearchNeed seeds,
WorkUnit seeds, candidate drafts, evidence drafts, pack drafts, review items,
or pack exports. Outputs must not be accepted public records, observed baseline
truth, accepted evidence truth, master-index mutations, rights clearance,
malware safety, verified installability, exhaustive search proof, or production
readiness claims.

## Validation

Run:

```powershell
python scripts/validate_eureka_workunit_result.py
```

The validator is stdlib-only and read-only.
