# Implementation Start Recommendation

## Recommendation

Start with `INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT`, then implement
`INDEXLESS-LIVE-SEARCH-FALLBACK-00` as a constrained run mode.

## Why Not Start With Full `SEMANTIC-CORE-CONTRACTS-00`

`TSIS-00` has already added semantic, action, route, representation, view, and
policy contracts. A fresh semantic-core task would risk duplicating existing
repo authority. The next implementation step should first verify gaps against
the existing contract set.

## Why Not Start With Full Greenfield `RESOLVER-SPINE-00`

The repo already has resolution-run runtime paths and tests. The safer task is
to prove whether fallback can reuse those paths, then add only the minimum
missing behavior.

## First Task Shape

```text
Task ID: INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT

Goal:
Verify the exact existing seams for implementing indexless live fallback as a
ResolutionRunKernel mode, without runtime behavior changes.

Outputs:
- gap report
- allowed implementation paths
- focused test lane
- fallback acceptance checklist
- decision whether implementation can proceed directly
```

## Implementation Can Proceed When

- fallback has a single run entrypoint
- source output is `SourceObservation` only
- fallback output is candidate/need/blocked/unavailable only
- review is the only promotion path
- public/API/surface paths cannot call sources directly
- disable switches and budgets are testable

