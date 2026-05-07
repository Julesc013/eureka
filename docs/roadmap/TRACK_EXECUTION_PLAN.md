# Track Execution Plan

This plan records the post-AIDE convergence execution order for future Eureka
work. It is a compact pointer to the authoritative audit:

- `control/audits/eureka-convergence-v0/`

## Order

1. A0 - convergence / preflight
2. Track A - representation and view-model spine
3. Manual Observation Batch 0
4. Track B - Eureka Node, work units, candidates, source/evidence/review loop
5. Track D - snapshot and relay substrate
6. Track C - native clients
7. Track E - hosting and operations

## Next Task

`TRACK-A-08 - PackPage, TaskPage, and ReviewPage view model contracts`

Track A goes first because every later public, static, snapshot, relay, native,
and hosted surface needs the same representation, host-profile, compatibility,
evidence, and action vocabulary.

Track A-01 established the host/profile/representation contract bundle. Track
A-02 established the semantic renderer parity policy that constrains those
profiles before renderer or view-model runtime work widens. Track A-03 binds
route families to canonical view families, representation profiles, host
profiles, and semantic parity policies. Track A-04 established the canonical
SearchPage view-model contract that later renderer and runtime work must
preserve. Track A-05 established the canonical ObjectPage view-model contract
for object identity, source/evidence posture, member lineage, rights/risk
posture, and blocked action meaning. Track A-06 established the canonical
SourcePage view-model contract for source identity, policy/access posture,
connector-disabled status, source cache/evidence ledger posture, rights/risk/
privacy caution, and source coverage gaps. Track A-07 established the canonical
NeedPage and CandidatePage view-model contracts for scoped unresolved demand,
known absence, source gaps, provisional discoveries, review state, and
no-public-truth candidate posture.

Track D comes before Track C because native clients need stable snapshot and
relay substrate before project creation.

Track E remains last because actual hosted public alpha requires operator
evidence, deployment posture, DNS/TLS, abuse controls, rate limits, monitoring,
rollback, and claim traceability.

## Public Alpha Rule

Early public-alpha-shaped work in this repo means local, staged, static, or
localhost rehearsal evidence. Actual hosted public alpha is Track E only.

## Agent Operating Discipline

Future AIDE-driven tasks should keep documentation and behavior claims honest,
write task-local evidence under `.aide/queue/<TASK-ID>/`, use focused commits
with descriptive bodies, and update compact memory or queue state when the
result changes what future agents should know. This is an operating rule, not a
license for AIDE to own Eureka product semantics.
