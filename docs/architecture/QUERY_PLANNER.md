# Query Planner

Eureka should move from raw-query handling toward compiled resolution tasks.

## Why A Planner Exists

A user query such as `Windows 7 apps` is not only a string. It is a probable
task involving:

- an object type
- a likely action
- platform or time constraints
- likely false interpretations
- likely useful source lanes

Without a planner, users must do that investigation work manually.

## Compiled Query Shape

A compiled query should eventually capture structured intent such as:

- desired action
- desired object type
- platform constraints
- time constraints
- aliases
- explicit suppressions or negative constraints

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

## Planner Responsibilities

The investigation planner should turn compiled query information into:

- source lanes
- retrieval lanes
- bounded budgets
- remaining work
- excluded interpretations
- explanations that can be shown back to the user

## v0 Direction

The planned v0 query planner should be:

- deterministic
- rule-based
- stdlib-compatible in the current lane
- explicit about what it suppresses and why

It should not require LLMs or semantic infrastructure to be useful.
