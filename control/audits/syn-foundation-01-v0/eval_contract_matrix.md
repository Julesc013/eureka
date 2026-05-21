# Eval Contract Matrix

SYN-00 adds:

- `contracts/query/synthetic_query_case.v0.json`
- `contracts/query/synthetic_query_set.v0.json`

It also consumes existing query contracts:

- `contracts/query/search_quality_query_set.v0.json`
- `contracts/query/search_need_seed.v0.json`
- `contracts/query/workunit_seed.v0.json`

The contracts are fixture-shadow contracts and do not change runtime search, ranking, evidence, SearchNeed, WorkUnit, or public search behavior.
