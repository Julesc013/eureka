# Existing Truth Seams

| Seam | Disposition |
| --- | --- |
| E2E reference runner | Compose for synthetic run input. |
| ReviewQueueStore | Compose as isolated decision store. |
| Review Ledger | Compose through `record_review_ledger_decision(...)`. |
| Local review materialization | Exclude; preserve existing non-production behavior. |
| Synthetic materialization | Add isolated synthetic-only generation writer. |
| Local lexical search | Compose through local index document shape and search semantics. |
| Preview Index | Exclude from production authority; synthetic reviewed authority remains guarded. |
| Snapshot runtime | Compose offline manifest, envelope, fixity, and verification helpers. |
| Rollback | Implement pointer restoration over immutable generations. |

Conclusion: canonical decisions flow through ReviewQueueStore and Review Ledger. Materialized synthetic state is isolated and reversible.

