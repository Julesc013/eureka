# Review Batch Runtime

`REVIEW-BATCH-00` adds deterministic batch review over local candidate memory and SCOUT relation output.

The runtime groups candidates into review clusters, builds an operator-gated batch packet, validates batch decisions, creates state-update previews, and emits promotion-preview plus handoff packets.

Batch review does not create accepted truth. Promotion preview is not promotion. Local apply and snapshot refresh remain separate gates.

Public projections are read-only summaries. They expose cluster context but no accept, reject, promote, or mutation actions.
