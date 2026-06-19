# E2E Reference System Track

Task:

```text
E2E-REFERENCE-SYSTEM-TRACK-00
```

Status: `PASS`

## Purpose

Eureka is moving from individually validated source and evidence machinery to
one coherent local reference system. This track authorizes the safe sequence of
deterministic, non-truth-changing work needed to connect the pieces without
requiring a separate authority ceremony for every internal transformation.

The track starts with:

```text
E2E-REFERENCE-CONTRACT-00
```

## Milestone Boundary

`Source Foundry Preview v0` remains the validated checkpoint promoted to
`main`. It proves:

```text
IA metadata
-> source observations
-> provisional candidates
-> evidence summaries
-> review batch
-> explicit Review Ledger evidence requests
```

It does not claim reviewed IA truth, public exposure, production readiness, or
complete autonomous foundry behavior.

The next product milestone is:

```text
Eureka Local Reference System v0
```

## Six Planes

1. Discovery Plane
   Owns query intent, ResolutionRuns, Hunts, WorkUnits, scheduling, provider
   ports, budgets, timeouts, replay, retries, and partial failure.

2. Evidence Plane
   Owns SourceObservations, EvidenceSummaries, provenance, locators,
   conflicts, unavailability, absence, and near misses.

3. Preview Plane
   Owns status-aware projections across reviewed records, candidates, near
   misses, needs, absences, blocked states, unavailable states, and unknowns.

4. Truth Plane
   Owns ReviewItems, ReviewDecisions, the Review Ledger, ReviewedRecords,
   supersession, accepted local deltas, and review lineage.

5. Distribution Plane
   Owns local indexes, snapshots, relay, API, CLI, web, text/classic HTML,
   native projections, and agent-context packets.

6. Control and Observability Plane
   Owns AIDE, queue authority, policy, run events, health, metrics, validation,
   audit, release gates, rollback, and incident posture.

Cross-plane invariant:

```text
Discovery may propose.
Evidence may support.
Preview may project.
Review may decide.
Truth may materialize.
Distribution may publish permitted projections.
Control may constrain and verify.
No plane may silently assume another plane's authority.
```

## Child Sequence

```text
E2E-REFERENCE-CONTRACT-00
-> E2E-REFERENCE-RUNNER-00
-> E2E-PREVIEW-INDEX-00
-> E2E-HUNT-EXPLORATION-UI-00
-> SYNTHETIC-TRUTH-PATH-E2E-00
-> AUTONOMOUS-EVAL-ORACLE-00
-> PORTABLE-EUREKA-INSTANCE-00
-> HUMAN-END-TO-END-ACCEPTANCE-00
```

The second live-provider task and real review/index foundry work remain
separately gated.

## Autonomous Scope

This track pre-authorizes deterministic work for:

- contract consolidation
- stable identifiers and hashes
- state transitions
- recorded replay
- synthetic fixtures
- local run orchestration
- WorkUnit scheduling
- event logging
- preview-index generation
- result-lane assembly
- Workbench projections
- local CLI, API, and web integration
- fault injection
- deterministic recovery and rollback testing
- isolated synthetic truth mechanics
- evaluation harnesses
- local portable-instance wrappers
- documentation and runbooks
- focused tests and external validation handoffs

## Hard Gates

Separate authority remains required for:

- new live-provider or network access
- credentials or secrets
- real Review Ledger decisions
- real reviewed-record materialization
- reviewed/master-index mutation
- public-index mutation
- public snapshot publication
- public exposure
- public launch
- downloads or file payload fetching
- installation, emulation, or execution
- license changes
- destructive data migration
- native/mobile distribution
- Rust replacement of reference semantics

## Synthetic Truth Exception

Truth-changing mechanics may be tested only in a synthetic namespace when:

- stores are isolated;
- no real candidate is used;
- no production Review Ledger is used;
- no reviewed/master/public index is touched;
- rollback is mandatory;
- generated snapshots are test-only;
- outputs clearly identify synthetic authority.

## IA Review Batch Posture

The current IA review packet is frozen as:

```text
prepared
evidence-linked
partially dispositioned as request_more_evidence
not promoted
not discarded
available for later acceptance testing
```

Current counts:

| Item | Count |
| --- | ---: |
| Prepared IA candidates | 56 |
| Request-more-evidence decisions | 8 |
| Parent batch items pending | 48 |
| Promoted IA candidates | 0 |
| Reviewed records created | 0 |

The batch remains useful as an acceptance dataset, ranking test set, review UX
test set, evidence-acquisition seed, and provider-conformance set. It must not
be auto-decided, promoted, erased, or marked complete.

## Branch And Promotion Posture

`main` remains the validated Source Foundry Preview v0 checkpoint. `dev` now
contains the human-last operating decision and this track authority. Main
promotion is not part of this task.

## Deferred Work

These tasks are not pre-authorized here:

- second live provider
- real review and reviewed-index foundry
- public exposure or launch
- downloads, installation, emulation, or execution
- Rust replacement
- native/mobile distribution

