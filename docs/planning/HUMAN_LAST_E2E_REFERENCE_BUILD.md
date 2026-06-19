# Human-Last E2E Reference Build Decision

Task:

```text
HUMAN-LAST-E2E-REFERENCE-BUILD-00
```

Status: `PASS`

## Decision

Eureka adopts a human-last end-to-end reference-system operating model.

Routine human review of real candidates is paused while Eureka's coherent local
reference experience is built. Automation may validate every non-truth-changing
layer and may exercise truth-changing mechanics in an isolated synthetic
namespace. Real discoveries remain provisional until explicit human review.

This is human-last, not human-never. Product-level human calibration remains
appropriate at major milestones for interaction model, terminology, ranking
usefulness, privacy expectations, provider policy, and public exposure.

## Why

Source Foundry Preview v0 is complete and promoted to `main`:

```text
Source Foundry Preview v0 is functional and validated.
IA candidates remain unreviewed or evidence-requested.
No reviewed IA truth has been created.
Public exposure remains paused.
```

The next strategic transition is from individually valid source/evidence
machinery to one coherent local Eureka reference system.

## Current IA Review Packet Posture

The current IA review material is frozen as:

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
| Tranche 01 request-more-evidence decisions | 8 |
| Parent batch items still pending | 48 |
| Promoted IA candidates | 0 |
| Reviewed records created | 0 |

The batch may later be used as a real acceptance dataset, ranking test set,
review UX test set, evidence-acquisition seed, and provider-conformance set.

Do not erase it, auto-decide the remaining items, promote fixture-derived
records, or make it the main development bottleneck.

## Six-Plane Model

Use this architecture vocabulary for the next product milestone:

1. Discovery
2. Evidence
3. Preview
4. Truth
5. Distribution
6. Control and Observability

The Preview Plane is the key bridge. It should make reviewed records,
candidates, near misses, needs, absences, policy blocks, unavailable sources,
and unknown states searchable together without collapsing their authority.

## Automation Allowed

Automation may build and validate:

- discovery and run orchestration
- WorkUnit scheduling
- deterministic replay
- synthetic fixtures
- source observations
- evidence summaries
- candidate and preview indexes
- Workbench projections
- CLI, API, and web integration
- fault injection
- portable packaging
- evaluation harnesses
- rollback and recovery tests
- synthetic review, reviewed-record, index, and snapshot mechanics in an
  isolated namespace

## Human Gates Retained

These remain explicit hard gates:

- new live-provider or network approval
- real Review Ledger decisions
- reviewed-record materialization for real discoveries
- reviewed/master-index mutation
- public-index mutation
- downloads or execution
- public exposure
- license changes

## Next Sequence

Recommended next tasks:

```text
E2E-REFERENCE-SYSTEM-TRACK-00
E2E-REFERENCE-CONTRACT-00
E2E-REFERENCE-RUNNER-00
E2E-PREVIEW-INDEX-00
E2E-HUNT-EXPLORATION-UI-00
SYNTHETIC-TRUTH-PATH-E2E-00
AUTONOMOUS-EVAL-ORACLE-00
PORTABLE-EUREKA-INSTANCE-00
HUMAN-END-TO-END-ACCEPTANCE-00
E2E-SECOND-LIVE-PROVIDER-00
REAL-REVIEW-AND-INDEX-FOUNDRY-00
```

Core principle:

```text
Build one coherent, portable, end-to-end Eureka before scaling providers,
clients, indexes, or public deployment modes.
```

