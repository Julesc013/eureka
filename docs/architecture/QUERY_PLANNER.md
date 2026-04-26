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
- member/container discovery hints
- bounded manual lookup
- article-inside-scan and document-member search
- honest `generic_search` fallback when no bounded family matches

Old-Platform Software Planner Pack v0 extends this deterministic lane for the
selected usefulness wedge. It now records:

- OS aliases such as Windows 7 / Windows NT 6.1, Windows XP / NT 5.1, Windows
  2000 / NT 5.0, Win9x aliases, Mac OS 9, Mac OS X Tiger, and Snow Leopard
- platform-vs-target distinction so `Windows 7 apps` remains a software query
  with a Windows 7 compatibility constraint
- latest-compatible release intent without asserting the actual latest version
- driver + hardware + OS intent, including INF/support-media representation
  hints
- vague identity uncertainty for queries such as `old blue FTP client for XP`
- member/container hints for support CDs, ISOs, ZIPs, bundles, and packages
- manual/readme/documentation hints without adding OCR or document connectors
- app-vs-OS-media suppression hints such as `os_iso_image` and
  `operating_system_install_media`

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
- live source behavior or source connector execution
