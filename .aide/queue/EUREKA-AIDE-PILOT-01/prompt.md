# Compact Prompt Record

Implement the Q22 Eureka AIDE Lite import pilot inside `julesc013/eureka`.

Required result:

- Import the portable `aide-lite-pack-v0` without source AIDE queue history, generated context, reports, local state, raw prompts, raw responses, secrets, or source project memory.
- Initialize compact Eureka-specific AIDE memory.
- Generate Eureka-local snapshot, repo map, context packet, task packet, review packet, and token estimates.
- Prove prompt-size reduction against a local naive baseline using `chars / 4`.
- Write evidence under this queue item and leave the item ready for review.

This is a compact task record, not a raw prompt log.
