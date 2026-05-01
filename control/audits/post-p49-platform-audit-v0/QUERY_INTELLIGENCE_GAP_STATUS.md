# Query Intelligence Gap Status

| Capability | Evidence | Classification | Recommended order |
|---|---|---|---:|
| Query observation contract | not present as governed contract | `planning_only` | 10 |
| Shared query/result cache | local index exists, shared query cache absent | `deferred` | 11 |
| Miss ledger | bounded absence summaries only | `planning_only` | 12 |
| Search need record | no governed reusable search-need record | `planning_only` | 13 |
| Probe queue | live probe gateway contract only | `approval_gated` | 14 |
| Candidate index | fixture/local index only | `deferred` | 15 |
| Candidate promotion policy | review queue contracts exist, query promotion absent | `planning_only` | 16 |
| Known absence page | absence reports exist locally, public known-absence page absent | `planning_only` | 17 |
| Query privacy/poisoning guard | public search safety policy only | `contract_only` | 18 |
| Demand dashboard | absent | `deferred` | 19 |
| Public query learning runtime | absent | `deferred` | after 19 |

This is the biggest post-P49 platform gap. Fast learning is not yet wired to
slow truth: public misses do not become shared search needs, and public queries
do not update any privacy-filtered intelligence store.
