# Source Policy Decision Items

These items prepare future human/operator policy review. They are not source access decisions.

| Review item | Recommended decision | Status |
| --- | --- | --- |
| `review_item::source_gaps_to_source_policy_decisions` | `request_more_evidence` | Source policy review required |
| `review_item::policy_blocked_items_to_node_policy` | `mark_policy_blocked` | Blocked by policy |

## Boundary

- Do not treat source leads as permission to crawl, scrape, query APIs, run live probes, or sync sources.
- Do not approve live source access from this packet.
- Keep broad web, forum, and other restricted source ideas blocked until a separate policy decision exists.
