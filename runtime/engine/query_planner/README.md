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
- supports platform software search, vague software identity, latest-compatible release, driver and hardware-support lookup, manual lookup, and article-inside-scan patterns
- extracts compact platform, product, hardware, topic, and date hints
- records prefer and exclude hints plus bounded action and source hints
- returns `generic_search` when the query does not match a supported family
- can derive a current deterministic search string for planned search runs
- stays anchored to the current archive-resolution eval packet rather than claiming broad natural-language understanding

This slice does not yet provide:

- full investigation planning
- source budgets or planner phases
- streaming partial results
- planner-driven retrieval routing
- resolution memory
