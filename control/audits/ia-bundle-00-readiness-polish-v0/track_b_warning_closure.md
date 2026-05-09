# Track B Warning Closure

Track B remains `PASS_WITH_WARNINGS`, but IA-BUNDLE-00 closes or classifies the
warnings that could otherwise blur the IA start gate.

## Evidence Contract Location

Classification: closed by minimal contract pointer namespace.

`contracts/evidence_ledger/` already contains governed schema-only evidence
ledger contracts. IA-BUNDLE-00 adds `contracts/evidence/` as a pointer/index
namespace so future tasks can find evidence contract material without
duplicating the existing schemas.

No evidence runtime, write path, source-cache mutation, evidence acceptance,
candidate acceptance, or truth acceptance is enabled.

## Historical Active Merge And B22

Classification: superseded by canonical main baseline.

The Track B B22 active-merge warning is historical. The sync baseline records a
clean branch state, no active merge/rebase/cherry-pick/revert, and a canonical
main baseline.

Reference: `control/audits/sync-baseline-01-canonical-main-v0/baseline_report.json`.

## Historical OBS Hardening And Full-Test Warning

Classification: superseded by canonical main baseline.

The older OBS hardening/full-test warning is superseded by the sync baseline
recording full unittest discovery as `pass_2508_tests`.

Reference: `control/audits/sync-baseline-01-canonical-main-v0/baseline_report.json`.

## IA Connector Prerequisites

Classification: intentionally deferred.

IA source policy, User-Agent/contact, allowed and forbidden endpoint decisions,
rate limit, timeout/retry, cache TTL, kill switch, fixture normalizer, live
probe, source-cache write, evidence candidate conversion, review queue
integration, reviewed-index dry-run, quality delta, and postmortem remain in
IA-BUNDLE-01 through IA-BUNDLE-03.

IA-BUNDLE-00 does not approve source access and does not enable a connector.
