# Query Planner

Query Planner v0 is now implemented as Eureka's first deterministic rule-based
compiler from raw user text into a bounded `ResolutionTask`.

## Why A Planner Exists

A user query such as `Windows 7 apps` is not only a string. It is a probable
task involving:

- an object type
- a likely action
- platform or time constraints
- likely false interpretations
- likely useful source lanes

Without a planner, users must do that investigation work manually.

## Resolution Task Shape

The current task shape captures compact structured intent such as:

- task kind
- object type
- platform constraints
- time or year hints
- product, hardware, or document hints
- explicit prefer and exclude hints
- action and source hints
- planner confidence and notes

Example direction:

```text
raw_query: "Windows NT 6.1 apps"
-> action: browse_or_install
-> object type: application
-> platform family: Windows NT
-> platform version: 6.1
-> alias: Windows 7
-> suppress: operating system ISO images
```

## Current v0 Scope

The implemented v0 planner is:

- deterministic
- rule-based
- stdlib-compatible in the current lane
- explicit about what it knows and what it does not know

Supported query families now include:

- platform software search
- vague software identity
- latest-compatible release
- driver and hardware-support lookup
- bounded manual lookup
- article-inside-scan and document-member search
- honest `generic_search` fallback when no bounded family matches

## Current Integration

Resolution Run Model v0 now accepts an optional `resolution_task` summary for
planned-search runs. Query Planner v0 shapes that summary and derives the
current deterministic search string, but it does not yet own retrieval lanes,
budgets, source routing, checkpoints, or streaming phases.

Local Index v0 now exists as a separate retrieval substrate, but Query Planner
v0 does not yet route into it, choose between search modes, or own indexed
retrieval semantics.

## Still Deferred

Query Planner v0 does not yet provide:

- full investigation planning
- source-lane or retrieval-lane routing
- budgets, checkpoints, or remaining-work summaries
- planner-driven ranking or suppression beyond bounded prefer/exclude hints
- LLM planning
- vector or fuzzy retrieval
