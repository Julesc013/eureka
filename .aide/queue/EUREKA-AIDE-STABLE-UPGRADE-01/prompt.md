# Q55 Prompt Summary

Implement a controlled Eureka-local AIDE upgrade from the stable AIDE Lite
release bundle validated by Q54.

Use Q54 evidence as the source of truth. Preserve Eureka target state:
`.aide/memory/**`, `.aide/queue/**`, `.aide/context/latest-*` until locally
regenerated, `.aide/reports/eureka-*`, Eureka golden tasks, AGENTS manual
content, architecture checks, source/evidence/index validators, and product
source roots.

Allowed writes are limited to `.aide/**` plus narrowly permitted managed
guidance if needed. Do not mutate product files, branch/remotes, live source
systems, providers/models, public indexes, source caches, evidence ledgers,
release publishing, CI, or local private state.

Required outcome: a Q55 queue packet, preservation/sync/validation evidence,
updated top-level AIDE reports, and a Q56 task packet for `Q56 Eureka Existing
Tool Absorption`, with status ending at `needs_review`.
