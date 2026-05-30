# SCOUT Runtime

SCOUT is deterministic relation expansion over local candidate memory. It reads
`candidate_record.v0` records, infers local relationships, builds discovery
trails, projects related paths, creates source trust observations, and suggests
WorkUnit seeds.

SCOUT is not a crawler, not engagement ranking, not an AI browsing agent, and
not a promotion workflow. Outputs are review-required hints only.

Runtime boundaries:

```text
no live source calls
no crawling
no downloads
no extraction
no model/provider calls
no reviewed/master/public index mutation
no accepted truth
```
