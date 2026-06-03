# Hard Query Eval Plan

The hard-query eval proves usefulness before launch. It should compare Eureka's
reviewed/candidate/need output against expected answer shapes, not just keyword
hits.

## Required Output Per Query

Every failed query must create one of:

- SearchNeed
- near_miss
- policy_blocked
- known_absence
- concrete improvement task

## Initial Gate

Run after fallback implementation and before reviewed seed corpus launch gate.

