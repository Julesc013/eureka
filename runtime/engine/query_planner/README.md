# Query Planner

Query Planner v0 adds the first deterministic rule-based compiler from a raw
user query into a bounded `ResolutionTask`.

This slice is intentionally small:

- deterministic and stdlib-only
- no LLMs
- no vector search
- no fuzzy retrieval
- no ranking or planner-driven source routing
- no worker orchestration

Current Query Planner v0 behavior:

- classifies a bounded set of archive-resolution eval query families
- supports platform software search, vague software identity, latest-compatible
  release, driver and hardware-support lookup, member/container discovery,
  manual/documentation lookup, and article-inside-scan patterns
- normalizes bounded old-platform aliases including Windows 7 / Windows NT 6.1,
  Windows XP / NT 5.1, Windows 2000 / NT 5.0, Win9x aliases, Mac OS 9, and
  PowerPC Mac OS X 10.4
- treats queries like `Windows 7 apps` as software-for-platform requests rather
  than operating-system media requests
- extracts compact platform, product, hardware, function, representation,
  member-discovery, topic, date, temporal-goal, and uncertainty hints
- records prefer and exclude hints plus bounded action and source hints,
  including app-vs-OS-media suppression hints
- returns `generic_search` when the query does not match a supported family
- can derive a current deterministic search string for planned search runs
- stays anchored to the current archive-resolution eval packet rather than claiming broad natural-language understanding

Old-Platform Software Planner Pack v0 is implemented in this deterministic
rule lane. It improves interpretation only; it does not rank results, perform
fuzzy/vector retrieval, call live sources, use LLM planning, or route around
missing source evidence.

This slice does not yet provide:

- full investigation planning
- source budgets or planner phases
- streaming partial results
- planner-driven retrieval routing
- resolution memory
