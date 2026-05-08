# Local Evidence Ledger Runtime Plan

TRACK-B-14 defines the planning layer for a future local evidence ledger. It
does not implement evidence-ledger runtime, create local ledger directories,
write evidence records, bridge source-cache records into evidence, or accept
evidence.

## What It Is

A local evidence ledger is a future local/private append-style ledger for
evidence candidates, claim records, source observations, provenance links,
review status, conflict notes, and conversion records from reviewed
source-cache records into evidence candidates.

The current milestone is planning-only. The active phase is
`phase_0_planning_only`, runtime status is `runtime_not_implemented`,
source-cache bridge status is `source_cache_bridge_not_implemented`, and
evidence acceptance status is `evidence_acceptance_disabled`.

## What It Is Not

The local evidence ledger is not accepted evidence, public truth, a public
index, the master index, source-cache runtime, source sync, connector runtime,
raw payload storage, credential storage, telemetry, or production persistence.

Evidence ledger records are candidates and provenance events by default. They
must not claim rights clearance, malware safety, verified installability,
exhaustive global search, production readiness, accepted public record status,
or master-index mutation authority.

## Relationship To Existing Evidence Work

`docs/reference/EVIDENCE_LEDGER_CONTRACT.md` defines the evidence-ledger contract
boundary. Existing P99 local dry-run evidence-ledger tooling reports candidate
posture over synthetic repo examples only. B-14 adds the approval gates,
append-style semantics, and source-cache bridge plan that must exist before any
future authoritative local evidence-ledger runtime.

## Why It Follows Source Cache Planning

Source cache records are observations, not truth. Evidence ledger planning
defines the next boundary: how reviewed source-cache records may later become
evidence candidates with provenance, review status, conflict preservation, and
truth-boundary fields. The bridge is not implemented in B-14.

## Append-Style Intent

Future ledger behavior should preserve history:

- corrections append new records
- supersession appends new records
- conflicts are preserved
- provenance is required
- review status is required
- silent overwrite is forbidden
- unreviewed promotion is forbidden
- master-index mutation is forbidden

B-14 defines intent only. It creates no append storage.

## Review Gates

Review is required before candidate store use, public index use, pack export,
master-index review, rights claims, malware-safety claims, installability
claims, and source-cache bridge use.

Automatic evidence acceptance, public index use, master-index mutation, rights
clearance, malware-safety claims, and installability verification are forbidden.

## Path And Storage Boundary

B-14 documents future roots but does not create them:

- `.aide.local/eureka/evidence_ledger/`
- `.local/eureka/evidence_ledger/`
- `.cache/eureka/evidence_ledger/`

Current generated planning evidence may only use explicit audit output roots
such as `control/audits/**/generated/evidence_ledger/` or explicit temporary
test directories. `site/dist/`, `runtime/`, `contracts/`, `native/`,
`snapshots/`, publication inventory, master-index-related roots, `.git/`, and
private or credential paths are forbidden output roots.

## Validation

```bash
python scripts/validate_local_evidence_ledger_runtime_plan.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

The validator checks planning-only status, disabled bridge and acceptance
status, append policy, bridge forbidden conversions, examples, review gates,
truth and product boundaries, private paths, and credential-shaped text.
