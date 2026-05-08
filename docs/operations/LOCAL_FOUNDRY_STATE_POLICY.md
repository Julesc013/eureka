# Local Foundry State Policy

Local foundry state is private by default and export-gated by review.

## Allowed Future Uses

- record node reports and WorkUnit results
- record dry-run and validation reports
- hold observation candidates and source leads
- hold SearchNeed seeds and local candidate drafts
- hold source-cache and evidence-ledger drafts
- hold review queue and pack-builder drafts
- hold local index, snapshot, and relay previews

These are policy-scoped future uses only. This task creates no local state and
does not enable a runtime.

## Forbidden Uses

- store credentials, account sessions, raw browser profiles, telemetry streams,
  private user files, executable downloads, or installer payloads
- store accepted public records, accepted evidence truth, or master-index
  records as private drafts
- use local state to claim rights clearance, malware safety, verified
  installability, exhaustive search, or production readiness
- write local state into `contracts/`, `runtime/`, `surfaces/`, generated site
  artifacts, source inventories, publication inventories, or observed baseline
  roots
- export state publicly without review

## Git Tracking

Private state must not be tracked by Git. Audit reports may be committed.
Exported packs may be committed only after review. Private caches and
credentials must not be committed.

## Review Gates

Public export requires human review. Source policy, evidence, candidate, pack,
master-index, privacy, rights, and risk reviews apply before any local draft can
affect public or canonical records.

## Validation

Run:

```powershell
python scripts/validate_local_foundry_state.py
```
