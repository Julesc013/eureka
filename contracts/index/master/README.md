# Master Index Contracts

This directory contains contract-only schemas for future Eureka master-index
governance. These files do not implement hosted intake, uploads, accounts,
moderation UI, queue runtime, live source behavior, or master-index writes.

- `review_queue_manifest.v0.json` describes a queue manifest.
- `review_queue_entry.v0.json` describes one reviewable candidate entry.
- `review_decision.v0.json` describes a reviewer or future policy decision.

The current queue examples are synthetic and local validation fixtures only.
