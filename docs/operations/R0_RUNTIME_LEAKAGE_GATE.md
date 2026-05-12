# R0 Runtime Leakage Gate

R0-02 adds a static gate for task, prompt, audit, bundle, and preview wording in
production-looking paths. It is an audit and guard task only. It does not
refactor runtime modules, move contracts, delete H-series artifacts, call live
sources, or change product behavior.

## Run The Gate

Check mode:

```bash
python scripts/audit_runtime_architecture_leakage.py --check --json
```

Write explicit sample outputs:

```bash
python scripts/audit_runtime_architecture_leakage.py \
  --output control/audits/r0-02-runtime-architecture-leakage-gate-v0/generated/sample_leakage_gate_report.json \
  --summary-output control/audits/r0-02-runtime-architecture-leakage-gate-v0/generated/sample_leakage_summary.md
```

Validate the policy, allowlist, generated reports, and no-product-path boundary:

```bash
python scripts/validate_runtime_architecture_leakage.py
```

Enforce mode:

```bash
python scripts/audit_runtime_architecture_leakage.py --enforce --json
```

`--enforce` is stricter than `--check`: it fails for expired allowlist entries
as well as new unallowlisted production-path leaks.

## What Fails

The gate fails when a production-looking path contains a forbidden term that is
not already recorded as exact temporary remediation debt. Production-looking
paths include `runtime/**`, `surfaces/**`, `site/**`, `native/**`, `crates/**`,
and public/product-shaped contract paths.

The gate also refuses to write outputs under forbidden product roots. R0-02
outputs belong under `control/inventory/`, `control/audits/r0-02-.../`,
`control/policies/`, or the R0 docs paths.

## Allowlists

The allowlist records existing leaks by exact path, term, line, column, and
context hash. That means existing R0-02 debt can be reported without blocking
the current branch, while a fresh copy of the same vocabulary in a new location
fails check mode.

Allowlist entries must include:

- a reason
- an owner
- a replacement
- an expiry task
- a severity after expiry

Entries should expire when the remediation task has had a chance to remove or
quarantine the debt. Existing contract taxonomy debt generally expires after
`R0-03`. Existing runtime naming debt generally expires after `R0-04`.

## Choosing Remediation

Use the report outputs in this order:

1. `control/inventory/runtime_architecture_leakage_gate_report.json`
2. `control/inventory/runtime_architecture_leakage_blockers.json`
3. `control/inventory/runtime_architecture_leakage_remediation_plan.json`
4. `control/audits/r0-02-runtime-architecture-leakage-gate-v0/known_violations.md`

If the dominant leaks are contract schemas, continue to `R0-03 — Contract
taxonomy refactor`. If the dominant leaks are runtime package or symbol names,
continue to `R0-04 — Source observation production seam` or split a focused
leakage remediation task first.

## Why R0-02 Does Not Fix Leaks

R0-02 creates the guard. It deliberately avoids moving contracts, renaming
runtime packages, or deleting generated scaffold so the current state remains
auditable. Future R0 tasks can now refactor with a machine-readable baseline
and a hard failure mode for new task-shaped product architecture.

F0 remains blocked. Dev-to-main promotion remains blocked.
